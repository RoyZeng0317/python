a = int(input("請輸入第一個數字: "))
b = int(input("請輸入第二個數字: "))

result = 1
arr = []

for i in range(1, min(a, b) + 1):
    if a % i == 0 and b % i == 0:
        result = i
        arr.append(i)

print("所有公因數:", arr)
print("最大公因數為:", result)