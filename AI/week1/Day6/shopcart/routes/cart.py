from flask import Blueprint, request, jsonify, session
from db import get_conn, put_conn

cart_bp = Blueprint('cart', __name__)

def login_required():
    return 'user_id' in session

@cart_bp.route('/api/cart', methods=['GET'])
def get_cart():
    if not login_required():
        return jsonify(success=False, message='請先登入', error='未提供有效的 Token'), 401

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ci.id, ci.product_id, p.name, p.price, ci.quantity,
                       (p.price * ci.quantity) AS subtotal, p.image_url
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.user_id = %s
                ORDER BY ci.created_at
            """, (session['user_id'],))
            rows = cur.fetchall()

            items = [{
                'id': r[0], 'product_id': r[1], 'product_name': r[2],
                'price': float(r[3]), 'quantity': r[4],
                'subtotal': float(r[5]), 'image_url': r[6]
            } for r in rows]

            total = sum(item['subtotal'] for item in items)
            count = sum(item['quantity'] for item in items)

            return jsonify(success=True, data={
                'cart_items': items, 'total_amount': total, 'item_count': count
            }), 200
    except Exception as e:
        return jsonify(success=False, message='無法取得購物車', error=str(e)), 500
    finally:
        put_conn(conn)

@cart_bp.route('/api/cart', methods=['POST'])
def add_to_cart():
    if not login_required():
        return jsonify(success=False, message='請先登入', error='未提供有效的 Token'), 401

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify(success=False, message='加入購物車失敗', error='請提供商品 ID'), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT stock, name, price FROM products WHERE id = %s', (product_id,))
            product = cur.fetchone()
            if not product:
                return jsonify(success=False, message='加入購物車失敗', error='商品不存在'), 404
            if product[0] < quantity:
                return jsonify(success=False, message='加入購物車失敗', error=f'庫存不足，目前庫存：{product[0]}'), 400

            cur.execute(
                'SELECT id, quantity FROM cart_items WHERE user_id = %s AND product_id = %s',
                (session['user_id'], product_id)
            )
            existing = cur.fetchone()

            if existing:
                new_qty = existing[1] + quantity
                if new_qty > product[0]:
                    return jsonify(success=False, message='加入購物車失敗', error=f'庫存不足，目前庫存：{product[0]}'), 400
                cur.execute(
                    'UPDATE cart_items SET quantity = %s WHERE id = %s',
                    (new_qty, existing[0])
                )
                cart_item_id = existing[0]
            else:
                cur.execute(
                    'INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s) RETURNING id',
                    (session['user_id'], product_id, quantity)
                )
                cart_item_id = cur.fetchone()[0]

            conn.commit()

            cur.execute(
                'SELECT ci.id, ci.product_id, p.name, p.price, ci.quantity, (p.price * ci.quantity) AS subtotal '
                'FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.id = %s',
                (cart_item_id,)
            )
            r = cur.fetchone()

            return jsonify(success=True, message='已加入購物車', data={
                'cart_item_id': r[0], 'product_id': r[1],
                'product_name': r[2], 'quantity': r[4], 'subtotal': float(r[5])
            }), 201
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='加入購物車失敗', error=str(e)), 500
    finally:
        put_conn(conn)

@cart_bp.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart(item_id):
    if not login_required():
        return jsonify(success=False, message='請先登入', error='未提供有效的 Token'), 401

    data = request.get_json()
    quantity = data.get('quantity')

    if not quantity or quantity < 1:
        return jsonify(success=False, message='更新失敗', error='數量必須大於 0'), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT ci.id, p.stock FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.id = %s AND ci.user_id = %s',
                (item_id, session['user_id'])
            )
            item = cur.fetchone()
            if not item:
                return jsonify(success=False, message='更新失敗', error='購物車項目不存在'), 404
            if quantity > item[1]:
                return jsonify(success=False, message='更新失敗', error=f'庫存不足，目前庫存：{item[1]}'), 400

            cur.execute('UPDATE cart_items SET quantity = %s WHERE id = %s', (quantity, item_id))
            conn.commit()

            return jsonify(success=True, message='數量已更新', data={
                'cart_item_id': item_id, 'quantity': quantity
            }), 200
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='更新失敗', error=str(e)), 500
    finally:
        put_conn(conn)

@cart_bp.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    if not login_required():
        return jsonify(success=False, message='請先登入', error='未提供有效的 Token'), 401

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'DELETE FROM cart_items WHERE id = %s AND user_id = %s',
                (item_id, session['user_id'])
            )
            if cur.rowcount == 0:
                return jsonify(success=False, message='移除失敗', error='購物車項目不存在'), 404
            conn.commit()
            return jsonify(success=True, message='已從購物車移除'), 200
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='移除失敗', error=str(e)), 500
    finally:
        put_conn(conn)
