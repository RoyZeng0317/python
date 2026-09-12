"""
==================================================
第三單元：迴圈與重複執行 (Loops & Iteration)
==================================================
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. for 迴圈與 range()
print("--- 1. for 迴圈與 range(start, stop, step) ---")
# 印出 1 到 5 的偶數/奇數
print("range(1, 6):", list(range(1, 6)))

total = 0
for i in range(1, 11):  # 1 到 10
    total += i
print(f"1 加到 10 的總和為: {total}")

# 2. enumerate 與 zip
print("\n--- 2. enumerate (帶索引迴圈) 與 zip (平行走訪) ---")
fruits = ["蘋果", "香蕉", "橘子"]
prices = [30, 15, 25]

for idx, fruit in enumerate(fruits, start=1):
    print(f"第 {idx} 個水果: {fruit}")

print("\n--- 使用 zip 配對水果與價格 ---")
for fruit, price in zip(fruits, prices):
    print(f"{fruit}: {price} 元")

# 3. while 迴圈與 break / continue
print("\n--- 3. while 迴圈與 break / continue ---")
count = 0
while count < 5:
    count += 1
    if count == 3:
        print("遇到 3，跳過 (continue)")
        continue
    print(f"目前 count = {count}")

# 4. 九九乘法表實作 (巢狀迴圈)
print("\n--- 4. 九九乘法表 ---")
for i in range(1, 4):  # 展示前 3 排
    row = [f"{i}x{j}={i*j:2d}" for j in range(1, 10)]
    print(" | ".join(row))
