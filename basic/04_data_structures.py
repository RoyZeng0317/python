"""
==================================================
第四單元：四大核心資料結構 (Data Structures)
==================================================
List (列表), Tuple (元組), Dictionary (字典), Set (集合)
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 列表 (List): 可變、有序
print("--- 1. List (列表) 與切片 ---")
numbers = [10, 20, 30, 40, 50]
numbers.append(60)       # 末尾新增
numbers[0] = 99          # 修改元素
print(f"修改後的 List: {numbers}")
print(f"前三項 (切片 [:3]): {numbers[:3]}")
print(f"最後一項 ([-1]): {numbers[-1]}")

# List 推導式 (List Comprehension)
squares = [x**2 for x in range(1, 6)]
print(f"1~5 平方列表推導式: {squares}")

# 2. 元組 (Tuple): 不可變、有序
print("\n--- 2. Tuple (元組) ---")
point = (10, 20)  # (x, y) 座標
x, y = point      # 解構賦值 (Unpacking)
print(f"座標: {point}, x={x}, y={y}")

# 3. 字典 (Dictionary): Key-Value 鍵值對、可變
print("\n--- 3. Dictionary (字典) ---")
student = {
    "name": "Bob",
    "age": 18,
    "scores": [88, 92, 95]
}
student["city"] = "Taipei"  # 新增鍵值對
print(f"學生姓名: {student['name']}")
print(f"學生平均分數: {sum(student['scores']) / len(student['scores']):.1f}")
print("字典所有的 Key-Value:")
for key, value in student.items():
    print(f"  {key}: {value}")

# 4. 集合 (Set): 唯一、無序 (自動去重)
print("\n--- 4. Set (集合) 與集合運算 ---")
raw_data = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique_data = set(raw_data)
print(f"原始列表: {raw_data}")
print(f"去重後的 Set: {unique_data}")

set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
print(f"交集 (a & b): {set_a & set_b}")
print(f"聯集 (a | b): {set_a | set_b}")
print(f"差集 (a - b): {set_a - set_b}")
