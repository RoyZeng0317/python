# sql 版
import os
import mysql.connector

conn = mysql.connector.connect(
    host = "localhost",
    user = "boyud9.5",
    pwd = "",
    database = "database"
)
cursor = conn.cursor()
cursor.execute("SELECT name, price, age_limit FROM products WHERE barcode = %s", (barcode,))
result = cursor.fetchone()

pd_name = ["冰鎮檸檬紅茶-535ml", "冰鎮花果茶"]
pd_bd = ["4710095951502", "47110096961603", "4710946578193", "47155178466644717546061667","4710946578193"]
pd_price = [29, 35]
alcohol_name = ["再見南國-芒果風味"]
alchol_bd = ["4711588006747", ""]
alcohol_price = [140]
香菸_bd = ["47100535312345"]
香菸_name = ["尊爵香菸"]
香菸_price = [95]
total = 0

def 結帳():
    while True:    
        global total
        barcode = input("請輸入條碼-> ")

        if barcode.lower == "q":
            break

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
            age_check = int(input("是否18歲-> "))
            result = bool(age_check)
            if result == False:
                print("抱歉，因未成年而無法購買")
            else:
                print(f"商品:{alcohol_name[index]}", f"價格:{money}元", f"總額:{total}")
        elif barcode in 香菸_bd:
            index = 香菸_bd.index(barcode)
            money = 香菸_price[index]
            total += money
            print(f"商品:{香菸_bd[index]}", "此商品為菸品，需要確認是否年滿二十歲")
            age_check = int(input("是否十八歲-> "))
            result = bool(age_check)
            if result == False:
                print("抱歉，因為符合購買年紀而無法購買")
            else:
                print(f"商品:{alcohol_name[index]}", f"價格:{money}元", f"總額:{total}")
        else:
            print("查無商品")
結帳()