# 階乘
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)

n = int(input("請輸入數字 n: "))
print("結果:", factorial(n))