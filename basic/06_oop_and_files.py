"""
==================================================
第六與第七單元：物件導向 (OOP) 與 檔案/錯誤處理 (Files & Exceptions)
==================================================
"""
import sys
import io
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 類別 (Class) 與 物件 (Object)
print("--- 1. 物件導向 (OOP) 類別與方法 ---")

class BankAccount:
    """簡單銀行帳戶類別"""
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: float):
        if amount > 0:
            self.balance += amount
            print(f"[{self.owner}] 成功存款 ${amount}，最新餘額: ${self.balance}")
        else:
            print("存款金額必須大於 0")

    def withdraw(self, amount: float) -> bool:
        if amount > self.balance:
            print(f"[{self.owner}] 提款失敗: 餘額不足 (${self.balance})")
            return False
        self.balance -= amount
        print(f"[{self.owner}] 成功提款 ${amount}，剩餘餘額: ${self.balance}")
        return True

# 測試類別實體化與呼叫
acc = BankAccount("Roy", 1000)
acc.deposit(500)
acc.withdraw(300)
acc.withdraw(2000)  # 觸發餘額不足

# 2. 例外處理 (Try-Except)
print("\n--- 2. 例外處理 (Try-Except-Finally) ---")
def safe_divide(a, b):
    try:
        res = a / b
    except ZeroDivisionError:
        print("錯誤: 除數不能為 0！")
        return None
    except TypeError:
        print("錯誤: 輸入型態必須為數字！")
        return None
    else:
        print(f"計算成功: {a} / {b} = {res}")
        return res

safe_divide(10, 2)
safe_divide(10, 0)

# 3. 檔案讀寫 (File I/O)
print("\n--- 3. 檔案讀寫實作 ---")
filename = "basic_demo_output.txt"

# 寫入檔案
with open(filename, "w", encoding="utf-8") as f:
    f.write("Python 基礎學習紀錄\n")
    f.write("1. 變數與型態\n")
    f.write("2. 邏輯與迴圈\n")
    f.write("3. 資料結構與 OOP\n")
print(f"已寫入資料至檔案: {filename}")

# 讀取檔案
print("\n讀取檔案內容:")
with open(filename, "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 清理測試檔案
if os.path.exists(filename):
    os.remove(filename)
    print(f"測試檔 {filename} 已清理完成")
