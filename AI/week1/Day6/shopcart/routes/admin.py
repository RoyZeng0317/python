from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from db import get_conn, put_conn
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if username != Config.ADMIN_USERNAME or password != Config.ADMIN_PASSWORD:
        return jsonify(success=False, message='管理員登入失敗', error='帳號或密碼錯誤，或無管理員權限'), 401

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, username, password_hash FROM users WHERE username = %s AND role = %s',
                (username, 'admin')
            )
            user = cur.fetchone()
            if not user:
                return jsonify(success=False, message='管理員登入失敗', error='帳號或密碼錯誤，或無管理員權限'), 401

            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = 'admin'
            session['is_admin'] = True

            return jsonify(success=True, message='管理員登入成功', data={
                'admin_id': user[0], 'username': user[1], 'role': 'admin'
            }), 200
    except Exception as e:
        return jsonify(success=False, message='管理員登入失敗', error=str(e)), 500
    finally:
        put_conn(conn)

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def dashboard():
    if not session.get('is_admin'):
        return jsonify(success=False, message='存取被拒', error='僅限管理員存取'), 403

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM users')
            total_users = cur.fetchone()[0]

            cur.execute('SELECT COUNT(*) FROM orders')
            total_orders = cur.fetchone()[0]

            cur.execute('SELECT COALESCE(SUM(total_amount), 0) FROM orders')
            total_revenue = float(cur.fetchone()[0])

            cur.execute("""
                SELECT u.id, u.username, u.email, COALESCE(SUM(o.total_amount), 0) AS total_spent, COUNT(o.id) AS order_count
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                WHERE u.role = 'user'
                GROUP BY u.id
                ORDER BY total_spent DESC
            """)
            user_spending = [{
                'user_id': r[0], 'username': r[1], 'email': r[2],
                'total_spent': float(r[3]), 'order_count': r[4]
            } for r in cur.fetchall()]

            cur.execute("""
                SELECT o.id, u.username, o.total_amount, o.status, o.created_at
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC LIMIT 10
            """)
            recent_orders = [{
                'order_id': r[0], 'username': r[1],
                'total_amount': float(r[2]), 'status': r[3],
                'created_at': r[4].isoformat() if r[4] else None
            } for r in cur.fetchall()]

            return jsonify(success=True, data={
                'total_users': total_users, 'total_orders': total_orders,
                'total_revenue': total_revenue,
                'users_spending': user_spending, 'recent_orders': recent_orders
            }), 200
    except Exception as e:
        return jsonify(success=False, message='無法取得儀表板資料', error=str(e)), 500
    finally:
        put_conn(conn)
