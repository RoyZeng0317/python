"""
==================================================
第二單元：條件判斷與邏輯控制 (Control Flow & Logic)
==================================================
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 基礎 if / elif / else 判斷
score = 85

print("--- 1. 成績評等範例 ---")
print(f"目前分數: {score}")

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
elif score >= 60:
    grade = "D"
else:
    grade = "F"

print(f"評等結果: {grade}")

# 2. 邏輯運算子 (and, or, not)
print("\n--- 2. 邏輯運算子範例 ---")
age = 22
has_license = True
is_drunk = False

# 判斷是否能合法駕駛
can_drive = (age >= 18) and has_license and (not is_drunk)
print(f"年齡 {age}, 有駕照: {has_license}, 喝酒: {is_drunk}")
print(f"是否能開車: {can_drive}")

# 3. 三元運算子 (Ternary Operator / 簡寫 if-else)
status = "及格" if score >= 60 else "不及格"
print(f"\n三元運算子判斷: {score} 分 -> {status}")
