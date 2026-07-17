# 資料庫連線
import sqlite3

pd_name = ["冰鎮檸檬紅茶-535ml", "冰鎮花果茶"]
pd_bd = ["4710095951502", "47110096961603"]
pd_price = [29, 35]
alcohol_name = ["再見南國-芒果風味"]
alchol_bd = ["4710095951234"]
alcohol_price = [140]
total = 0
def 結帳():
    global total
    barcode = input("請輸入條碼-> ")

    if barcode in pd_bd:
        index = pd_bd.index(barcode)
        money = pd_price[index]
        total += money
        print(f"商品:{pd_name[index]}", f"價格:{money}元", f"總額:{total}元")
    elif barcode in alchol_bd:
        index = alchol_bd.index(barcode)
        money = alcohol_price[index]
        total += money
        print(f"商品:{alcohol_name[index]}", "此商品為酒精飲品，需確認是否年滿十八歲")
        age_check = bool(input("是否18歲-> "))
        if age_check == False:
            print("抱歉，因未成年而無法購買")
        else:
            print(f"商品:{alcohol_name[index]}", f"價格:{money}元", f"總額:{total}")
    else:
        print("查無商品")
    

結帳()