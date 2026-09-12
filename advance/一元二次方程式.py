import math
import numpy as np
import matplotlib.pyplot as plt

a = float(input("請輸入 value a: "))
b = float(input("請輸入 value b: "))
c = float(input("請輸入 value c: "))

d = b ** 2 - 4 * a * c
if d > 0:
    x1 = (-b + math.sqrt(d)) / (2 * a)
    x2 = (-b + math.sqrt(d)) / (2 * a)
    print("解一:", x1, "解二:", x2)
elif d == 0:
    x = -b / (2 * a)
    print("唯一解:", x)
else:
    print("無實數解")