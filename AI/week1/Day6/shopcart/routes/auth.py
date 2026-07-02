from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_conn, put_conn
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify(success=False, message='註冊失敗', error='所有欄位皆為必填'), 400
    if len(username) < 2 or len(username) > 50:
        return jsonify(success=False, message='註冊失敗', error='使用者名稱長度需為 2-50 字元'), 400
    if len(password) < 6:
        return jsonify(success=False, message='註冊失敗', error='密碼長度至少 6 字元'), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
            if cur.fetchone():
                return jsonify(success=False, message='註冊失敗', error='使用者名稱或 Email 已存在'), 400

            password_hash = generate_password_hash(password)
            cur.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id',
                (username, email, password_hash)
            )
            user_id = cur.fetchone()[0]
            conn.commit()

            return jsonify(success=True, message='註冊成功', data={
                'user_id': user_id, 'username': username, 'email': email
            }), 201
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='註冊失敗', error=str(e)), 500
    finally:
        put_conn(conn)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify(success=False, message='登入失敗', error='請輸入帳號與密碼'), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, username, email, password_hash, role FROM users WHERE username = %s', (username,))
            user = cur.fetchone()
            if not user or not check_password_hash(user[3], password):
                return jsonify(success=False, message='登入失敗', error='使用者名稱或密碼錯誤'), 401

            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]

            return jsonify(success=True, message='登入成功', data={
                'user_id': user[0], 'username': user[1], 'email': user[2],
                'token': session.sid
            }), 200
    except Exception as e:
        return jsonify(success=False, message='登入失敗', error=str(e)), 500
    finally:
        put_conn(conn)

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify(success=True, message='已成功登出'), 200
