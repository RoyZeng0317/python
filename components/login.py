# 延續這個庫的方式進行續寫，嚴禁任何的變更與刪除
# 下方註解表示功能需求，嚴禁刪除
# 不能使用任何 javascript 語言且需要使用 python 庫
import httpx, sqlite3, os, sys

DB_PATH = os.path.normpath("users.db")

def verify_login(acc, pwd):
    # 從 DB 當中讀取到的使用者進行帳戶比對
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM users WHERE account = ? AND password = ?",
        (acc, pwd),
    )
    matched = cursor.fetchone()
    conn.close()
    return matched is not None

def main():
    acc = input("請輸入帳戶：").strip()
    pwd = input("請輸入密碼：").strip()

    if verify_login(acc, pwd): # 當帳戶與 DB 比對成功(即有在資料庫)，此處需續寫
        print("輸入TOTP驗證碼或使用指紋識別")
    else:
        print("帳戶或密碼有誤!請重新輸入")

if __name__ == "__main__":
    main()