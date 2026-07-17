sum = 0

def 結帳():
    money = int(input("請輸入收款金額:"))
    banlace = money - sum
    print(f"找:{banlace}元")

結帳()