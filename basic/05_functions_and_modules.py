"""
==================================================
第五單元：函式與模組化 (Functions & Modules)
==================================================
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 基本函式定義與預設參數
print("--- 1. 函式定義與預設參數 ---")

def greet(name: str, msg: str = "你好") -> str:
    """產生招呼語的函式"""
    return f"{msg}，{name}！"

print(greet("Charlie"))
print(greet("David", msg="早安"))

# 2. *args (不定數量的位置引數) 與 **kwargs (不定數量的關鍵字引數)
print("\n--- 2. *args 與 **kwargs ---")

def calculate_stats(*numbers, **user_info):
    print(f"使用者資訊: {user_info}")
    if not numbers:
        return 0, 0
    total = sum(numbers)
    avg = total / len(numbers)
    return total, avg

sum_val, avg_val = calculate_stats(10, 20, 30, 40, user_name="Eve", role="Admin")
print(f"計算結果 -> 總和: {sum_val}, 平均: {avg_val:.2f}")

# 3. Lambda 匿名函式與 sorted 應用
print("\n--- 3. Lambda 匿名函式 ---")
students = [
    {"name": "Alice", "score": 88},
    {"name": "Bob", "score": 95},
    {"name": "Charlie", "score": 72}
]

# 按成績排序 (高到低)
sorted_students = sorted(students, key=lambda s: s["score"], reverse=True)
print("按成績由高到低排序:")
for s in sorted_students:
    print(f"  {s['name']}: {s['score']} 分")
