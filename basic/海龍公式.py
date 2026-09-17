from sympy import sqrt, Rational

a = int(input("請輸入三角形邊長 a-> "))
b = int(input("請輸入三角形邊長 b-> "))
c = int(input("請輸入三角形邊長 c-> "))

s = Rational(a + b + c, 2)
A = sqrt(s * (s - a) * (s - b) * (s - c))   # type: ignore
print(f"半周長-> {s}")
print(f"三角形面積為-> {A}")