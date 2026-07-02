import os
from flask import Flask, render_template
from config import Config
from db import init_db, close_db
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.checkout import checkout_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

app.register_blueprint(auth_bp)
app.register_blueprint(products_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/products/<int:product_id>')
def product_detail_page(product_id):
    return render_template('product_detail.html', product_id=product_id)

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/checkout')
def checkout_page():
    return render_template('checkout.html')

@app.route('/admin/login')
def admin_login_page():
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard_page():
    return render_template('admin/dashboard.html')

if __name__ == '__main__':
    try:
        init_db()
        app.run(host='127.0.0.1', port=8097, debug=True)
    finally:
        close_db()
