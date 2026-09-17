<<<<<<< Updated upstream
# 因為輸入 valut is 整數，而不是字串所以前面要 int        
I = int(input("請輸入電流:"))
R = int(input("請輸入電阻:"))
V = I * R
C = int(input("請輸入電容:"))
# 使用 switch case
options = int(input("選擇要計算的題目:"))

match options:
    case 1:
        # 歐姆定律
        print("根據歐姆定律得出電壓為:", V)
    case 2:
        # 電功率
        P = V * I
        print("電功率為:", P)
    case 3:
        Q = C * V
        print("庫侖定律:", Q)
    case 4:
        f = int(input("請輸入頻率:"))
        L = int(input("請輸入電感值:"))
        pi = 3.14
        omega = 2 * pi * f
        if(omega != None):
            xL = omega * L
            xC = omega * 1 / (omega * L)
        else:
            xL = 2 * pi * f * L
            xC = 1 / (2 * pi * f * C)
=======
import math, tkinter as tk

f = ["歐姆定律", "電功率", "庫侖定律", "焦耳定律"]

def main():
    for i in range(len(f)):
        print(f"{i + 1}. {f[i]}" )
    int(input("請選擇您要計算的題目:"))

def DC():
    global V
    # 因為輸入 value is 整數，而不是字串所以前面要 int        
    I = int(input("請輸入電流:"))
    R = int(input("請輸入電阻:"))
    C = int(input("請輸入電容:"))
    # 使用 switch case
    options = int(input("選擇要計算的題目:"))

    match options:
        case 1:
            V = I * R
            # 歐姆定律
            print("根據歐姆定律得出電壓為:", V)
            return V
        case 2:
            # 電功率
            P = V * I
            print("電功率為:", P)
        case 3:
            Q = C * V
            print("庫侖定律:", Q)
        case 4:
            # break
            ...
def AC():
    f = int(input("請輸入頻率:"))
    L = int(input("請輸入電感值:"))
    C = int(input("請輸入電容值:"))
    omega = 2 * math.pi * f
    if(omega != None):
        xL = omega * L
        xC = omega * 1 / (omega * L)
        print("電感阻抗: ", xL, "電容阻抗", xC)
    else:
        xL = 2 * math.pi * f * L
        xC = 1 / (2 * math.pi * f * C)

if __name__ == "__main__":
    main()
>>>>>>> Stashed changes
