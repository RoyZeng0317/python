const API_BASE = '/api';

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function showMessage(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `message ${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

async function apiFetch(url, options = {}) {
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };
    const res = await fetch(`${API_BASE}${url}`, config);
    return res.json();
}

function updateNav() {
    const username = sessionStorage.getItem('username');
    const authLinks = document.getElementById('auth-links');
    const userInfo = document.getElementById('user-info');
    const navUsername = document.getElementById('nav-username');

    if (username && authLinks && userInfo) {
        authLinks.style.display = 'none';
        userInfo.style.display = 'flex';
        navUsername.textContent = `Hi, ${username}`;
    }
}

async function updateCartCount() {
    const badge = document.getElementById('cart-count');
    if (!badge) return;
    const username = sessionStorage.getItem('username');
    if (!username) { badge.textContent = '0'; return; }
    try {
        const res = await apiFetch('/cart');
        if (res.success) badge.textContent = res.data.item_count;
    } catch { badge.textContent = '0'; }
}

document.addEventListener('DOMContentLoaded', () => {
    updateNav();
    updateCartCount();
});

document.addEventListener('click', (e) => {
    if (e.target.id === 'logout-btn') {
        e.preventDefault();
        apiFetch('/auth/logout', { method: 'POST' }).then(() => {
            sessionStorage.clear();
            window.location.href = '/';
        });
    }
});

// Home page - hot products
if (document.getElementById('hot-products')) {
    apiFetch('/products/hot').then(res => {
        if (!res.success) return;
        const grid = document.getElementById('hot-products');
        grid.innerHTML = res.data.products.map(p => `
            <div class="product-card">
                <img src="${p.image_url || '/static/images/placeholder.svg'}" alt="${p.name}"
                     onerror="this.src='/static/images/placeholder.svg'">
                <div class="product-info">
                    <h3>${p.name}</h3>
                    <div class="price">NT$${p.price.toFixed(2)}</div>
                    <div class="description">${p.description || ''}</div>
                    <a href="/products/${p.id}" class="btn btn-primary btn-small">查看詳情</a>
                </div>
            </div>
        `).join('');
    });
}

// Login form
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const res = await apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (res.success) {
            sessionStorage.setItem('username', res.data.username);
            sessionStorage.setItem('user_id', res.data.user_id);
            showMessage('登入成功');
            setTimeout(() => window.location.href = '/', 500);
        } else {
            showMessage(res.error || res.message, 'error');
        }
    });
}

// Register form
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const res = await apiFetch('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });
        if (res.success) {
            showMessage('註冊成功，請登入');
            setTimeout(() => window.location.href = '/login', 800);
        } else {
            showMessage(res.error || res.message, 'error');
        }
    });
}

// Products page
const allProductsGrid = document.getElementById('all-products');
if (allProductsGrid) {
    let currentPage = 1;
    let currentCategory = 'all';
    let currentSort = '';

    function loadProducts() {
        let url = `/products?page=${currentPage}&limit=12`;
        if (currentCategory !== 'all') url += `&category=${currentCategory}`;
        if (currentSort) url += `&sort=${currentSort}`;

        apiFetch(url).then(res => {
            if (!res.success) return;
            allProductsGrid.innerHTML = res.data.products.map(p => `
                <div class="product-card">
                    <img src="${p.image_url || '/static/images/placeholder.svg'}" alt="${p.name}"
                         onerror="this.src='/static/images/placeholder.svg'">
                    <div class="product-info">
                        <h3>${p.name}</h3>
                        <div class="price">NT$${p.price.toFixed(2)}</div>
                        <div class="description">${p.description || ''}</div>
                        <a href="/products/${p.id}" class="btn btn-primary btn-small">查看詳情</a>
                    </div>
                </div>
            `).join('');

            const totalPages = Math.ceil(res.data.total / res.data.limit);
            const pagination = document.getElementById('pagination');
            pagination.innerHTML = '';
            for (let i = 1; i <= totalPages; i++) {
                const btn = document.createElement('button');
                btn.textContent = i;
                if (i === currentPage) btn.classList.add('active');
                btn.onclick = () => { currentPage = i; loadProducts(); };
                pagination.appendChild(btn);
            }
        });
    }

    document.getElementById('category-filter')?.addEventListener('change', (e) => {
        currentCategory = e.target.value;
        currentPage = 1;
        loadProducts();
    });

    document.getElementById('sort-by')?.addEventListener('change', (e) => {
        currentSort = e.target.value;
        currentPage = 1;
        loadProducts();
    });

    loadProducts();
}

// Product detail page
const detailSection = document.getElementById('product-detail');
if (detailSection) {
    const productId = typeof PRODUCT_ID !== 'undefined' ? PRODUCT_ID : null;
    if (productId) {
        apiFetch(`/products/${productId}`).then(res => {
            if (!res.success) {
                detailSection.innerHTML = '<p class="empty-cart">找不到該商品</p>';
                return;
            }
            const p = res.data;
            detailSection.innerHTML = `
                <img src="${p.image_url || '/static/images/placeholder.svg'}" alt="${p.name}"
                     onerror="this.src='/static/images/placeholder.svg'">
                <div class="detail-info">
                    <h2>${p.name}</h2>
                    <div class="price">NT$${p.price.toFixed(2)}</div>
                    <div class="description">${p.description || '暫無描述'}</div>
                    <div class="stock">庫存：${p.stock} 件</div>
                    <div class="form-group">
                        <label for="qty">數量：</label>
                        <input type="number" id="qty" value="1" min="1" max="${p.stock}">
                    </div>
                    <button class="btn btn-primary" id="add-to-cart-btn">加入購物車</button>
                </div>
            `;

            document.getElementById('add-to-cart-btn').addEventListener('click', async () => {
                if (!sessionStorage.getItem('username')) {
                    showMessage('請先登入', 'error');
                    setTimeout(() => window.location.href = '/login', 800);
                    return;
                }
                const qty = parseInt(document.getElementById('qty').value) || 1;
                const res = await apiFetch('/cart', {
                    method: 'POST',
                    body: JSON.stringify({ product_id: productId, quantity: qty })
                });
                if (res.success) {
                    showMessage('已加入購物車');
                    updateCartCount();
                } else {
                    showMessage(res.error || res.message, 'error');
                }
            });
        });
    }
}

// Cart page
const cartContent = document.getElementById('cart-content');
if (cartContent) {
    async function loadCart() {
        if (!sessionStorage.getItem('username')) {
            cartContent.innerHTML = '<p class="empty-cart">請先<a href="/login">登入</a>以查看購物車</p>';
            return;
        }
        const res = await apiFetch('/cart');
        if (!res.success) {
            cartContent.innerHTML = `<p class="empty-cart">${res.error || '無法載入購物車'}</p>`;
            return;
        }
        if (res.data.cart_items.length === 0) {
            cartContent.innerHTML = '<p class="empty-cart">購物車是空的，<a href="/products">去逛逛</a></p>';
            return;
        }
        cartContent.innerHTML = res.data.cart_items.map(item => `
            <div class="cart-item" data-id="${item.id}">
                <img src="${item.image_url || '/static/images/placeholder.svg'}" alt="${item.product_name}"
                     onerror="this.src='/static/images/placeholder.svg'">
                <div class="item-info">
                    <h3>${item.product_name}</h3>
                    <div class="price">NT$${item.price.toFixed(2)}</div>
                    <div class="subtotal">小計：NT$${item.subtotal.toFixed(2)}</div>
                </div>
                <div class="item-controls">
                    <input type="number" value="${item.quantity}" min="1" class="cart-qty" data-id="${item.id}">
                    <button class="btn btn-danger btn-small remove-item" data-id="${item.id}">移除</button>
                </div>
            </div>
        `).join('') + `
            <div class="cart-total">
                總計：<span>NT$${res.data.total_amount.toFixed(2)}</span>
            </div>
            <div style="text-align:right;margin-top:1rem;">
                <a href="/checkout" class="btn btn-primary">前往結帳</a>
            </div>
        `;

        document.querySelectorAll('.cart-qty').forEach(input => {
            input.addEventListener('change', async (e) => {
                const itemId = e.target.dataset.id;
                const qty = parseInt(e.target.value) || 1;
                const res = await apiFetch(`/cart/${itemId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ quantity: qty })
                });
                if (res.success) {
                    showMessage('數量已更新');
                    loadCart();
                    updateCartCount();
                } else {
                    showMessage(res.error || res.message, 'error');
                    loadCart();
                }
            });
        });

        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const itemId = e.target.dataset.id;
                const res = await apiFetch(`/cart/${itemId}`, { method: 'DELETE' });
                if (res.success) {
                    showMessage('已移除商品');
                    loadCart();
                    updateCartCount();
                } else {
                    showMessage(res.error || res.message, 'error');
                }
            });
        });
    }
    loadCart();
}

// Checkout page
const checkoutForm = document.getElementById('checkout-form');
if (checkoutForm) {
    async function loadOrderSummary() {
        if (!sessionStorage.getItem('username')) {
            document.getElementById('order-summary').innerHTML = '<p>請先登入</p>';
            return;
        }
        const res = await apiFetch('/cart');
        if (!res.success || res.data.cart_items.length === 0) {
            document.getElementById('order-summary').innerHTML = '<p>購物車為空</p>';
            return;
        }
        document.getElementById('order-summary').innerHTML = res.data.cart_items.map(item => `
            <div class="order-summary-item">
                <span>${item.product_name} x${item.quantity}</span>
                <span>NT$${item.subtotal.toFixed(2)}</span>
            </div>
        `).join('') + `
            <div class="order-total">
                <span>總計</span>
                <span>NT$${res.data.total_amount.toFixed(2)}</span>
            </div>
        `;
    }
    loadOrderSummary();

    checkoutForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const shipping_address = document.getElementById('shipping_address').value;
        const phone = document.getElementById('phone').value;
        const payment_method = document.getElementById('payment_method').value;

        if (!payment_method) {
            showMessage('請選擇付款方式', 'error');
            return;
        }

        const res = await apiFetch('/checkout', {
            method: 'POST',
            body: JSON.stringify({ shipping_address, phone, payment_method })
        });
        if (res.success) {
            showMessage('訂單已成立！感謝您的購買！');
            updateCartCount();
            setTimeout(() => window.location.href = '/', 1500);
        } else {
            showMessage(res.error || res.message, 'error');
        }
    });
}

// Admin login
const adminLoginForm = document.getElementById('admin-login-form');
if (adminLoginForm) {
    adminLoginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const res = await apiFetch('/admin/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
        if (res.success) {
            sessionStorage.setItem('is_admin', 'true');
            showMessage('管理員登入成功');
            setTimeout(() => window.location.href = '/admin/dashboard', 500);
        } else {
            showMessage(res.error || res.message, 'error');
        }
    });
}

// Admin dashboard
if (document.getElementById('stat-users')) {
    if (!sessionStorage.getItem('is_admin')) {
        window.location.href = '/admin/login';
    } else {
        apiFetch('/admin/dashboard').then(res => {
            if (!res.success) {
                showMessage(res.error || '請重新登入', 'error');
                sessionStorage.removeItem('is_admin');
                setTimeout(() => window.location.href = '/admin/login', 1000);
                return;
            }
            const d = res.data;
            document.getElementById('stat-users').textContent = d.total_users;
            document.getElementById('stat-orders').textContent = d.total_orders;
            document.getElementById('stat-revenue').textContent = `NT$${d.total_revenue.toFixed(2)}`;

            const userTbody = document.querySelector('#user-spending-table tbody');
            userTbody.innerHTML = d.users_spending.map(u => `
                <tr>
                    <td>${u.username}</td>
                    <td>${u.email}</td>
                    <td>NT$${u.total_spent.toFixed(2)}</td>
                    <td>${u.order_count}</td>
                </tr>
            `).join('');

            const orderTbody = document.querySelector('#recent-orders-table tbody');
            orderTbody.innerHTML = d.recent_orders.map(o => `
                <tr>
                    <td>#${o.order_id}</td>
                    <td>${o.username}</td>
                    <td>NT$${o.total_amount.toFixed(2)}</td>
                    <td>${o.status === 'pending' ? '待處理' : o.status}</td>
                    <td>${o.created_at ? new Date(o.created_at).toLocaleString('zh-TW') : '-'}</td>
                </tr>
            `).join('');
        });
    }
}

document.getElementById('admin-logout-btn')?.addEventListener('click', (e) => {
    e.preventDefault();
    sessionStorage.removeItem('is_admin');
    window.location.href = '/admin/login';
});

// Placeholder SVG for missing images
const placeholderSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
    <rect fill="#f0f0f0" width="400" height="400"/>
    <text fill="#ccc" font-size="24" font-family="sans-serif" x="50%" y="50%" text-anchor="middle" dy=".3em">暫無圖片</text>
</svg>`;
