"""
==================================================
第一單元：變數、資料型態與基本運算 (Variables & Data Types)
==================================================
"""
import sys
import io

# 確保在 Windows 控制台中正常輸出 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# 1. 變數宣告與印出
name = "Alice"       # 字串 (str)
age = 20            # 整數 (int)
height = 168.5      # 浮點數 (float)
is_student = True   # 布林值 (bool)

print("--- 1. 基本宣告與資料型態 ---")
print(f"姓名: {name}, 型態: {type(name)}")
print(f"年齡: {age}, 型態: {type(age)}")
print(f"身高: {height}, 型態: {type(height)}")
print(f"是否為學生: {is_student}, 型態: {type(is_student)}")

# 2. 型態轉換 (Type Casting)
print("\n--- 2. 型態轉換 ---")
num_str = "100"
num_int = int(num_str)          # 字串轉整數
num_float = float(num_str)      # 字串轉浮點數
back_to_str = str(num_int)      # 整數轉字串

print(f"字串 {num_str!r} 轉整數: {num_int} (型態: {type(num_int)})")
print(f"字串 {num_str!r} 轉浮點數: {num_float} (型態: {type(num_float)})")

# 3. 基本算術運算
print("\n--- 3. 算術運算 ---")
x = 10
y = 3

print(f"{x} + {y} = {x + y}")     # 加法
print(f"{x} - {y} = {x - y}")     # 減法
print(f"{x} * {y} = {x * y}")     # 乘法
print(f"{x} / {y} = {x / y}")     # 除法 (結果為浮點數)
print(f"{x} // {y} = {x // y}")   # 整除 (取商數)
print(f"{x} % {y} = {x % y}")     # 取餘數
print(f"{x} ** {y} = {x ** y}")   # 次方 (10 的 3 次方)

# 4. 字串格式化 (f-string 技巧)
print("\n--- 4. f-string 高級排版技巧 ---")
pi = 3.14159265
price = 1250
print(f"圓周率保留兩位小數: {pi:.2f}")
print(f"金額加上千分位格式: {price:,} 元")
