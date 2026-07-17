color = ["黑", "棕", "紅", "橙", "黃", "綠", "藍", "紫", "灰", "白"]
value = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, None]
誤差顏色 = ["金", "銀", "無"]
誤差值 = ["+/-5%", "+/-10%", "+/-20%"]
options = int(input("選擇要轉換的格式:"))

match options:
    case 1:
        # 顏色轉數值
        colors = input("請輸入共四個顏色(用空格分開): ").split()

        if len(color) == 4:
            print("請輸入共四個顏色 !") # 需要輸入四個顏色
        elif len(color) == 3:
            print("請輸入共三個顏色 !")
        else:
            print("請輸入共五個顏色 !")
        
        print("轉換結果為: ")

    case 2:
        # 數值轉顏色
        print("")