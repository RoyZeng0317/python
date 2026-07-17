import math

a, b = 12, 20

f = ["取餘數", "取商", "取相加", "取相減"]

for i in range(4):
    print(f[i])

o = int(input("選擇計算功能-> "))

match o:
    case 1:
        c = a % b
    case 2:
        c = a / b
    case 3:
        c = a + b
    case 4:
        c = a - b

print(c)
#  {-b +/- sqrt{b^2-4ac}}/2a
d = math.sqrt(b ** 2) - (4 * a * c)
if d > 0:
    (-b + d) / (2 * a)
else:
    (-b - d) / (2 * a)
print(d)