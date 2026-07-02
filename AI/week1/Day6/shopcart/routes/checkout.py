from flask import Blueprint, request, jsonify, session
from db import get_conn, put_conn

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/api/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify(success=False, message='請先登入', error='未提供有效的 Token'), 401

    data = request.get_json()
    shipping_address = data.get('shipping_address', '').strip()
    phone = data.get('phone', '').strip()
    payment_method = data.get('payment_method', '').strip()

    if not shipping_address or not phone or not payment_method:
        return jsonify(success=False, message='結帳失敗', error='請填寫收貨地址、電話與付款方式'), 400

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT ci.product_id, ci.quantity, p.name, p.price, p.stock
                FROM cart_items ci
                JOIN products p ON ci.product_id = p.id
                WHERE ci.user_id = %s
            """, (session['user_id'],))
            cart_items = cur.fetchall()

            if not cart_items:
                return jsonify(success=False, message='結帳失敗', error='購物車為空，無法結帳'), 400

            for item in cart_items:
                if item[2] > item[4]:
                    return jsonify(success=False, message='結帳失敗', error=f'商品「{item[2]}」庫存不足'), 400

            total_amount = sum(item[2] * item[1] for item in cart_items)

            cur.execute("""
                INSERT INTO orders (user_id, total_amount, shipping_address, phone, payment_method)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """, (session['user_id'], total_amount, shipping_address, phone, payment_method))
            order_id = cur.fetchone()[0]

            items_data = []
            for item in cart_items:
                product_id, qty, name, price, _ = item
                subtotal = price * qty
                cur.execute("""
                    INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (order_id, product_id, name, qty, price, subtotal))
                cur.execute('UPDATE products SET stock = stock - %s WHERE id = %s', (qty, product_id))
                items_data.append({
                    'product_name': name, 'quantity': qty,
                    'price': float(price), 'subtotal': float(subtotal)
                })

            cur.execute('DELETE FROM cart_items WHERE user_id = %s', (session['user_id'],))
            conn.commit()

            return jsonify(success=True, message='訂單已成立，感謝您的購買！', data={
                'order_id': order_id, 'total_amount': float(total_amount),
                'items': items_data, 'order_status': 'pending'
            }), 201
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='結帳失敗', error=str(e)), 500
    finally:
        put_conn(conn)
