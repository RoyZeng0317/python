from flask import Blueprint, request, jsonify
from db import get_conn, put_conn

products_bp = Blueprint('products', __name__)

@products_bp.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    category = request.args.get('category', '')
    sort = request.args.get('sort', '')
    offset = (page - 1) * limit

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            count_sql = 'SELECT COUNT(*) FROM products'
            sql = 'SELECT id, name, description, price, image_url, stock, is_hot, category FROM products'
            params = []
            conditions = []

            if category and category != 'all':
                conditions.append('category = %s')
                params.append(category)

            if conditions:
                where = ' WHERE ' + ' AND '.join(conditions)
                count_sql += where
                sql += where

            if sort == 'price_asc':
                sql += ' ORDER BY price ASC'
            elif sort == 'price_desc':
                sql += ' ORDER BY price DESC'
            else:
                sql += ' ORDER BY id ASC'

            sql += ' LIMIT %s OFFSET %s'
            params.extend([limit, offset])

            cur.execute(count_sql, params[:len(params)-2] if params[:len(params)-2] else [])
            total = cur.fetchone()[0]

            cur.execute(sql, params)
            rows = cur.fetchall()

            products = [{
                'id': r[0], 'name': r[1], 'description': r[2],
                'price': float(r[3]), 'image_url': r[4],
                'stock': r[5], 'is_hot': r[6], 'category': r[7]
            } for r in rows]

            return jsonify(success=True, data={
                'products': products, 'total': total, 'page': page, 'limit': limit
            }), 200
    except Exception as e:
        return jsonify(success=False, message='無法取得商品列表', error=str(e)), 500
    finally:
        put_conn(conn)

@products_bp.route('/api/products/hot', methods=['GET'])
def get_hot_products():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, name, description, price, image_url, stock, is_hot FROM products WHERE is_hot = TRUE LIMIT 5'
            )
            rows = cur.fetchall()
            products = [{
                'id': r[0], 'name': r[1], 'description': r[2],
                'price': float(r[3]), 'image_url': r[4],
                'stock': r[5], 'is_hot': r[6]
            } for r in rows]
            return jsonify(success=True, data={'products': products}), 200
    except Exception as e:
        return jsonify(success=False, message='無法取得熱門商品', error=str(e)), 500
    finally:
        put_conn(conn)

@products_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, name, description, price, image_url, stock, is_hot, category, created_at FROM products WHERE id = %s',
                (product_id,)
            )
            r = cur.fetchone()
            if not r:
                return jsonify(success=False, message='找不到該商品', error='商品 ID 不存在'), 404

            return jsonify(success=True, data={
                'id': r[0], 'name': r[1], 'description': r[2],
                'price': float(r[3]), 'image_url': r[4],
                'stock': r[5], 'is_hot': r[6], 'category': r[7],
                'created_at': r[8].isoformat() if r[8] else None
            }), 200
    except Exception as e:
        return jsonify(success=False, message='無法取得商品資訊', error=str(e)), 500
    finally:
        put_conn(conn)
