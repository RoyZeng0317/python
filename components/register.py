# 延續這個庫的方式進行續寫，嚴禁任何的變更與刪除
# 下方註解表示功能需求，嚴禁刪除
# 不能使用任何 javascript 語言且需要使用 python 庫
import sqlite3, os, sys

DB_PATH = os.path.normpath("users.db")

def init_db():
    # 確保 users 資料表存在，供 login.py / register.py 共用
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (account TEXT PRIMARY KEY, password TEXT NOT NULL)"
    )
    conn.commit()
    conn.close()

def register_user(acc, pwd):
    # 將新帳號寫入 DB，帳號重複則註冊失敗
    init_db()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO users (account, password) VALUES (?, ?)", (acc, pwd))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def main():
    acc = input("請輸入欲註冊的帳戶：").strip()
    pwd = input("請輸入密碼：").strip()

    if register_user(acc, pwd):
        print("註冊成功！")
    else:
        print("帳戶已存在，請重新輸入")

if __name__ == "__main__":
    main()
