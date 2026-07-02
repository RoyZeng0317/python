# 🛒 購物車系統 API 設計文件

## 1. 專案概述

| 項目 | 說明 |
|------|------|
| **專案名稱** | ShopCart 購物車系統 |
| **專案描述** | 一個完整的電子商務購物車網站，具備商品瀏覽、購物車管理、結帳功能及管理員後台儀表板。前端使用 HTML + CSS + JavaScript，後端使用 Python Flask 框架，資料庫採用 PostgreSQL，並透過連線池（Connection Pool）管理資料庫連線。 |
| **技術棧** | HTML5, CSS3, JavaScript (原生), Python 3, Flask, PostgreSQL (pgAdmin), psycopg2 (Connection Pool), python-dotenv |
| **伺服器埠號** | 8097 |
| **存取限制** | 僅限本地網路（localhost） |
| **資料庫連線池** | 使用 `psycopg2.pool.ThreadedConnectionPool` 或 `SimpleConnectionPool` |

---

## 2. 基礎 URL

```
http://localhost:8097/api
```

所有 API 端點均以此為前綴。回應格式皆為 `application/json`。

---

## 3. 認證 API（Authentication）

### 3.1 使用者註冊

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/auth/register` |

**Request Body：**
```json
{
    "username": "roy",
    "email": "roy@example.com",
    "password": "SecureP@ss123"
}
```

**Success Response（201 Created）：**
```json
{
    "success": true,
    "message": "註冊成功",
    "data": {
        "user_id": 1,
        "username": "roy",
        "email": "roy@example.com"
    }
}
```

**Error Response（400 Bad Request）：**
```json
{
    "success": false,
    "message": "註冊失敗",
    "error": "使用者名稱或 Email 已存在"
}
```

---

### 3.2 使用者登入

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/auth/login` |

**Request Body：**
```json
{
    "username": "roy",
    "password": "SecureP@ss123"
}
```

**Success Response（200 OK）：**
```json
{
    "success": true,
    "message": "登入成功",
    "data": {
        "user_id": 1,
        "username": "roy",
        "email": "roy@example.com",
        "token": "session_token_abc123"
    }
}
```

**Error Response（401 Unauthorized）：**
```json
{
    "success": false,
    "message": "登入失敗",
    "error": "使用者名稱或密碼錯誤"
}
```

---

### 3.3 使用者登出

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/auth/logout` |

**Request Headers：**
```
Authorization: Bearer <session_token>
```

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "message": "已成功登出"
}
```

**Error Response（401 Unauthorized）：**
```json
{
    "success": false,
    "message": "登出失敗",
    "error": "無效的 Token 或已過期"
}
```

---

## 4. 商品 API（Products）

### 4.1 取得所有商品列表

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `GET` |
| **URL 路徑** | `/api/products` |

**Request Query Parameters（可選）：**
```
?page=1&limit=10&category=all&sort=price_asc
```

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "id": 1,
                "name": "無線藍牙耳機",
                "description": "高音質降噪藍牙耳機，續航 24 小時",
                "price": 1299.00,
                "image_url": "/static/images/product_01.jpg",
                "stock": 50,
                "is_hot": true,
                "category": "電子產品"
            },
            {
                "id": 2,
                "name": "經典帆布後背包",
                "description": "簡約設計，大容量收納",
                "price": 890.00,
                "image_url": "/static/images/product_02.jpg",
                "stock": 100,
                "is_hot": true,
                "category": "包包配件"
            }
        ],
        "total": 15,
        "page": 1,
        "limit": 10
    }
}
```

**Error Response（500 Internal Server Error）：**
```json
{
    "success": false,
    "message": "無法取得商品列表",
    "error": "伺服器內部錯誤"
}
```

---

### 4.2 取得熱門商品（首頁用）

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `GET` |
| **URL 路徑** | `/api/products/hot` |

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "id": 1,
                "name": "無線藍牙耳機",
                "description": "高音質降噪藍牙耳機，續航 24 小時",
                "price": 1299.00,
                "image_url": "/static/images/product_01.jpg",
                "stock": 50,
                "is_hot": true
            },
            {
                "id": 2,
                "name": "經典帆布後背包",
                "description": "簡約設計，大容量收納",
                "price": 890.00,
                "image_url": "/static/images/product_02.jpg",
                "stock": 100,
                "is_hot": true
            },
            {
                "id": 3,
                "name": "有機綠茶禮盒",
                "description": "台灣高山茶葉，送禮自用兩相宜",
                "price": 680.00,
                "image_url": "/static/images/product_03.jpg",
                "stock": 30,
                "is_hot": true
            },
            {
                "id": 4,
                "name": "智能手環",
                "description": "心率監測、步數計算、來電提醒",
                "price": 1599.00,
                "image_url": "/static/images/product_04.jpg",
                "stock": 20,
                "is_hot": true
            },
            {
                "id": 5,
                "name": "桌上型小風扇",
                "description": "USB 供電，三段風速，靜音設計",
                "price": 350.00,
                "image_url": "/static/images/product_05.jpg",
                "stock": 80,
                "is_hot": true
            }
        ]
    }
}
```

**Error Response（500 Internal Server Error）：**
```json
{
    "success": false,
    "message": "無法取得熱門商品",
    "error": "伺服器內部錯誤"
}
```

---

### 4.3 取得單一商品詳細資料

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `GET` |
| **URL 路徑** | `/api/products/<int:product_id>` |

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "無線藍牙耳機",
        "description": "高音質降噪藍牙耳機，續航 24 小時，IPX5 防水",
        "price": 1299.00,
        "image_url": "/static/images/product_01.jpg",
        "stock": 50,
        "is_hot": true,
        "category": "電子產品",
        "created_at": "2026-06-15T10:30:00"
    }
}
```

**Error Response（404 Not Found）：**
```json
{
    "success": false,
    "message": "找不到該商品",
    "error": "商品 ID 不存在"
}
```

---

## 5. 購物車 API（Cart）

> 以下端點均需要在 Header 中帶入使用者 Token：
> `Authorization: Bearer <session_token>`

### 5.1 檢視購物車

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `GET` |
| **URL 路徑** | `/api/cart` |

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "data": {
        "cart_items": [
            {
                "id": 1,
                "product_id": 1,
                "product_name": "無線藍牙耳機",
                "price": 1299.00,
                "quantity": 2,
                "subtotal": 2598.00,
                "image_url": "/static/images/product_01.jpg"
            },
            {
                "id": 2,
                "product_id": 3,
                "product_name": "有機綠茶禮盒",
                "price": 680.00,
                "quantity": 1,
                "subtotal": 680.00,
                "image_url": "/static/images/product_03.jpg"
            }
        ],
        "total_amount": 3278.00,
        "item_count": 3
    }
}
```

**Error Response（401 Unauthorized）：**
```json
{
    "success": false,
    "message": "請先登入",
    "error": "未提供有效的 Token"
}
```

---

### 5.2 加入商品至購物車

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/cart` |

**Request Body：**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

**Success Response（201 Created）：**
```json
{
    "success": true,
    "message": "已加入購物車",
    "data": {
        "cart_item_id": 1,
        "product_id": 1,
        "product_name": "無線藍牙耳機",
        "quantity": 2,
        "subtotal": 2598.00
    }
}
```

**Error Response（400 Bad Request）：**
```json
{
    "success": false,
    "message": "加入購物車失敗",
    "error": "庫存不足，目前庫存：1"
}
```

---

### 5.3 更新購物車商品數量

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `PUT` |
| **URL 路徑** | `/api/cart/<int:item_id>` |

**Request Body：**
```json
{
    "quantity": 3
}
```

**Success Response（200 OK）：**
```json
{
    "success": true,
    "message": "數量已更新",
    "data": {
        "cart_item_id": 1,
        "product_id": 1,
        "quantity": 3,
        "subtotal": 3897.00
    }
}
```

**Error Response（404 Not Found）：**
```json
{
    "success": false,
    "message": "更新失敗",
    "error": "購物車項目不存在"
}
```

---

### 5.4 移除購物車商品

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `DELETE` |
| **URL 路徑** | `/api/cart/<int:item_id>` |

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "message": "已從購物車移除"
}
```

**Error Response（404 Not Found）：**
```json
{
    "success": false,
    "message": "移除失敗",
    "error": "購物車項目不存在"
}
```

---

## 6. 結帳 API（Checkout）

> 需要使用者 Token。

### 6.1 提交訂單

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/checkout` |

**Request Body：**
```json
{
    "shipping_address": "台北市大安區信義路四段 100 號 5 樓",
    "phone": "0912345678",
    "payment_method": "credit_card"
}
```

**Success Response（201 Created）：**
```json
{
    "success": true,
    "message": "訂單已成立，感謝您的購買！",
    "data": {
        "order_id": 1001,
        "total_amount": 3278.00,
        "items": [
            {
                "product_name": "無線藍牙耳機",
                "quantity": 2,
                "price": 1299.00,
                "subtotal": 2598.00
            },
            {
                "product_name": "有機綠茶禮盒",
                "quantity": 1,
                "price": 680.00,
                "subtotal": 680.00
            }
        ],
        "order_status": "pending",
        "created_at": "2026-07-02T14:30:00"
    }
}
```

**Error Response（400 Bad Request）：**
```json
{
    "success": false,
    "message": "結帳失敗",
    "error": "購物車為空，無法結帳"
}
```

---

## 7. 管理員 API（Admin）

### 7.1 管理員登入

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `POST` |
| **URL 路徑** | `/api/admin/login` |

**Request Body：**
```json
{
    "username": "admin",
    "password": "AdminP@ss456"
}
```

**Success Response（200 OK）：**
```json
{
    "success": true,
    "message": "管理員登入成功",
    "data": {
        "admin_id": 1,
        "username": "admin",
        "token": "admin_token_xyz789",
        "role": "admin"
    }
}
```

**Error Response（401 Unauthorized）：**
```json
{
    "success": false,
    "message": "管理員登入失敗",
    "error": "帳號或密碼錯誤，或無管理員權限"
}
```

---

### 7.2 取得儀表板統計資料

| 項目 | 值 |
|------|-----|
| **HTTP 方法** | `GET` |
| **URL 路徑** | `/api/admin/dashboard` |

**Request Headers：**
```
Authorization: Bearer <admin_token>
```

**Request Body：（無）**

**Success Response（200 OK）：**
```json
{
    "success": true,
    "data": {
        "total_users": 128,
        "total_orders": 356,
        "total_revenue": 485600.00,
        "users_spending": [
            {
                "user_id": 1,
                "username": "roy",
                "email": "roy@example.com",
                "total_spent": 15780.00,
                "order_count": 12
            },
            {
                "user_id": 2,
                "username": "alice",
                "email": "alice@example.com",
                "total_spent": 8900.00,
                "order_count": 5
            }
        ],
        "recent_orders": [
            {
                "order_id": 1001,
                "username": "roy",
                "total_amount": 3278.00,
                "status": "pending",
                "created_at": "2026-07-02T14:30:00"
            }
        ]
    }
}
```

**Error Response（403 Forbidden）：**
```json
{
    "success": false,
    "message": "存取被拒",
    "error": "僅限管理員存取"
}
```

---

## 8. 資料庫表格設計（Database Schema）

### 8.1 `users` 使用者資料表

| 欄位名稱 | 資料型態 | 限制 | 說明 |
|----------|----------|------|------|
| `id` | `SERIAL` | `PRIMARY KEY` | 使用者唯一識別碼 |
| `username` | `VARCHAR(50)` | `NOT NULL, UNIQUE` | 使用者名稱 |
| `email` | `VARCHAR(100)` | `NOT NULL, UNIQUE` | 電子郵件 |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | 密碼雜湊值（使用 bcrypt 或 werkzeug） |
| `role` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'user'` | 角色：`user` 或 `admin` |
| `phone` | `VARCHAR(20)` | | 電話號碼 |
| `address` | `TEXT` | | 預設收貨地址 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 建立時間 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新時間 |

**SQL 建立語法：**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 8.2 `products` 商品資料表

| 欄位名稱 | 資料型態 | 限制 | 說明 |
|----------|----------|------|------|
| `id` | `SERIAL` | `PRIMARY KEY` | 商品唯一識別碼 |
| `name` | `VARCHAR(200)` | `NOT NULL` | 商品名稱 |
| `description` | `TEXT` | | 商品描述 |
| `price` | `NUMERIC(10, 2)` | `NOT NULL` | 商品價格（台幣） |
| `image_url` | `VARCHAR(500)` | | 商品圖片路徑 |
| `stock` | `INTEGER` | `NOT NULL, DEFAULT 0` | 庫存數量 |
| `category` | `VARCHAR(100)` | | 商品分類 |
| `is_hot` | `BOOLEAN` | `DEFAULT FALSE` | 是否為熱門商品（首頁顯示） |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 建立時間 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新時間 |

**SQL 建立語法：**
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    image_url VARCHAR(500),
    stock INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(100),
    is_hot BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 8.3 `cart_items` 購物車項目資料表

| 欄位名稱 | 資料型態 | 限制 | 說明 |
|----------|----------|------|------|
| `id` | `SERIAL` | `PRIMARY KEY` | 購物車項目唯一識別碼 |
| `user_id` | `INTEGER` | `NOT NULL, REFERENCES users(id) ON DELETE CASCADE` | 使用者 ID（外鍵） |
| `product_id` | `INTEGER` | `NOT NULL, REFERENCES products(id) ON DELETE CASCADE` | 商品 ID（外鍵） |
| `quantity` | `INTEGER` | `NOT NULL, DEFAULT 1, CHECK(quantity > 0)` | 商品數量 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 加入時間 |

**唯一約束：** `UNIQUE(user_id, product_id)` — 同一使用者的同一商品不重複出現。

**SQL 建立語法：**
```sql
CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, product_id)
);
```

---

### 8.4 `orders` 訂單資料表

| 欄位名稱 | 資料型態 | 限制 | 說明 |
|----------|----------|------|------|
| `id` | `SERIAL` | `PRIMARY KEY` | 訂單唯一識別碼 |
| `user_id` | `INTEGER` | `NOT NULL, REFERENCES users(id) ON DELETE CASCADE` | 下單使用者 ID（外鍵） |
| `total_amount` | `NUMERIC(12, 2)` | `NOT NULL` | 訂單總金額 |
| `status` | `VARCHAR(20)` | `NOT NULL, DEFAULT 'pending'` | 訂單狀態：`pending` / `paid` / `shipped` / `completed` / `cancelled` |
| `shipping_address` | `TEXT` | | 收貨地址 |
| `phone` | `VARCHAR(20)` | | 聯絡電話 |
| `payment_method` | `VARCHAR(50)` | | 付款方式 |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 建立時間 |
| `updated_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | 更新時間 |

**SQL 建立語法：**
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_amount NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    shipping_address TEXT,
    phone VARCHAR(20),
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 8.5 `order_items` 訂單明細資料表

| 欄位名稱 | 資料型態 | 限制 | 說明 |
|----------|----------|------|------|
| `id` | `SERIAL` | `PRIMARY KEY` | 明細唯一識別碼 |
| `order_id` | `INTEGER` | `NOT NULL, REFERENCES orders(id) ON DELETE CASCADE` | 所屬訂單 ID（外鍵） |
| `product_id` | `INTEGER` | `NOT NULL, REFERENCES products(id) ON DELETE CASCADE` | 商品 ID（外鍵） |
| `product_name` | `VARCHAR(200)` | `NOT NULL` | 購買當下商品名稱（快照） |
| `quantity` | `INTEGER` | `NOT NULL` | 購買數量 |
| `unit_price` | `NUMERIC(10, 2)` | `NOT NULL` | 購買當下單價（快照） |
| `subtotal` | `NUMERIC(12, 2)` | `NOT NULL` | 小計 = quantity × unit_price |

**SQL 建立語法：**
```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(12, 2) NOT NULL
);
```

---

### 8.6 資料庫關係圖（ER 概述）

```
users (1) ────< (N) cart_items >──── (1) products
  │
  └─────────── (1) orders (1) ────< (N) order_items >──── (1) products
```

- 一個使用者可以有多個購物車項目、多筆訂單。
- 一筆訂單可以包含多個訂單明細。
- 購物車項目與訂單明細都關聯到商品資料。

---

## 9. 錯誤處理標準格式

所有 API 端點統一使用以下錯誤回應格式：

```json
{
    "success": false,
    "message": "人類可讀的簡短訊息",
    "error": "詳細錯誤說明或技術資訊（開發階段用）",
    "code": "ERROR_CODE_ENUM"
}
```

### 常用 HTTP 狀態碼對照

| 狀態碼 | 說明 | 使用情境 |
|--------|------|----------|
| `200 OK` | 請求成功 | 查詢、更新、刪除成功 |
| `201 Created` | 資源建立成功 | 註冊、加入購物車、建立訂單 |
| `400 Bad Request` | 請求格式錯誤或驗證失敗 | 缺少必填欄位、庫存不足 |
| `401 Unauthorized` | 未提供或提供無效 Token | 未登入、Token 過期 |
| `403 Forbidden` | 權限不足 | 非管理員存取後台 |
| `404 Not Found` | 資源不存在 | 商品 ID 或購物車項目 ID 錯誤 |
| `409 Conflict` | 資源衝突 | 重複註冊、重複加入購物車 |
| `500 Internal Server Error` | 伺服器內部錯誤 | 資料庫連線失敗、未預期例外 |

---

## 10. 安全性注意事項

### 10.1 環境變數（`.env`）

所有敏感資訊透過 `.env` 檔案管理，**請自行填入正確的值**，範例如下：

```env
# === 資料庫設定 ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=shopcart_db
DB_USER=postgres
DB_PASSWORD=你的資料庫密碼

# === 連線池設定 ===
DB_POOL_MIN_CONN=2
DB_POOL_MAX_CONN=10

# === Session / JWT 金鑰 ===
SECRET_KEY=請自行產生一組隨機金鑰
SESSION_EXPIRE_HOURS=24

# === 管理員預設帳號（首次啟動時建立） ===
ADMIN_USERNAME=admin
ADMIN_PASSWORD=請設定一組強密碼
```

> ⚠️ **重要：** `.env` 檔案**絕不可以**提交到 Git 儲存庫。請在首次使用前填寫所有欄位。

### 10.2 `.gitignore` 建議內容

```gitignore
# === 環境變數 ===
.env

# === Python 虛擬環境 ===
venv/
.venv/
env/

# === Python 快取 ===
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.egg-info/

# === IDE 設定 ===
.idea/
.vscode/
*.swp
*.swo

# === 作業系統檔案 ===
.DS_Store
Thumbs.db

# === 資料庫備份 ===
*.sql
*.dump

# === 日誌 ===
*.log
```

### 10.3 其他安全措施

| 項目 | 說明 |
|------|------|
| **密碼儲存** | 使用 `werkzeug.security.generate_password_hash()` 進行 bcrypt 或 PBKDF2 雜湊，**絕不儲存明文密碼** |
| **Session 管理** | 使用 Flask 內建 session 或 JWT Token，設定過期時間 |
| **SQL 注入防護** | 所有資料庫查詢使用參數化查詢（`cursor.execute("SQL %s", (param,))`），**禁止字串拼接** |
| **CORS 設定** | 限制僅允許 `http://localhost:8097` 來源存取 API |
| **本機存取限制** | Flask 設定 `host='127.0.0.1'`，僅限本機存取，不綁定 `0.0.0.0` |
| **輸入驗證** | 所有使用者輸入均在前端與後端雙重驗證長度、格式、型別 |
| **管理員路由保護** | 所有 `/api/admin/*` 路由需檢查 Token 與 `role == 'admin'` |

---

## 11. 附錄：前端頁面與 API 對應關係

| 前端頁面 | 路由 | 對應 API |
|----------|------|----------|
| **首頁** | `/` | `GET /api/products/hot` — 顯示 5 個熱門商品 |
| **註冊頁面** | `/register` | `POST /api/auth/register` |
| **登入頁面** | `/login` | `POST /api/auth/login` |
| **商品列表頁** | `/products` | `GET /api/products` |
| **商品詳情頁** | `/products/<id>` | `GET /api/products/<id>` |
| **購物車頁** | `/cart` | `GET /api/cart`、`POST /api/cart`、`PUT /api/cart/<id>`、`DELETE /api/cart/<id>` |
| **結帳頁** | `/checkout` | `POST /api/checkout` |
| **管理員登入頁** | `/admin/login` | `POST /api/admin/login` |
| **管理員儀表板** | `/admin/dashboard` | `GET /api/admin/dashboard` |

---

> **文件版本：** v1.0  
> **最後更新：** 2026-07-02  
> **設計者：** AI 輔助生成
