import math

x1 = int(input("請輸入座標 x1 -> "))
y1 = int(input("請輸入座標 y1 -> "))
x2 = int(input("請輸入座標 x2 -> "))
y2 = int(input("請輸入座標 y2 -> "))

d = math.sqrt(math.pow((x2 - x1), 2) + math.pow((y2 - y1), 2))

print(f"兩點之間的距離-> {d}")