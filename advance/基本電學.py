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