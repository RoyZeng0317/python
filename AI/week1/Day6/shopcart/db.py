import psycopg2
from psycopg2 import pool
from config import Config

connection_pool = None

def init_db():
    global connection_pool
    connection_pool = pool.ThreadedConnectionPool(
        Config.DB_POOL_MIN_CONN,
        Config.DB_POOL_MAX_CONN,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD
    )
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(open('schema.sql', 'r', encoding='utf-8').read())
            conn.commit()
    finally:
        put_conn(conn)

def get_conn():
    return connection_pool.getconn()

def put_conn(conn):
    connection_pool.putconn(conn)

def close_db():
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
