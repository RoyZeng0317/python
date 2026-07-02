import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'shopcart_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_POOL_MIN_CONN = int(os.getenv('DB_POOL_MIN_CONN', 2))
    DB_POOL_MAX_CONN = int(os.getenv('DB_POOL_MAX_CONN', 10))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SESSION_EXPIRE_HOURS = int(os.getenv('SESSION_EXPIRE_HOURS', 24))
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
