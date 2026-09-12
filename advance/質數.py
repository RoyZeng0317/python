a = int(input("請輸入起始數字: "))
b = int(input("請輸入終點數字: "))

arr = []

for num in range(a, b + 1):
    if num < 2:
        continue
    is_prime = True
    for i in range(2, num):
        if num % i == 0:
            is_prime = False
            break
    if is_prime:
        arr.append(num)

print("所有質數:", arr)