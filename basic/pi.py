import math

r = float(input("請輸入半徑:"))
cir = 2 * r * math.pi
d = r * 2
a = 1/4 * math.pi * (pow(d, 2))
print(f"圓周長: {cir}")
print(f"圓面積: {a}")