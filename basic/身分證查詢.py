# 建立字母與數字對照表
local_table = {'A': 1, 'B': 0, 'C': 0, 'D': 8, 'E': 7, 'F': 6, 'G': 5, 'H': 4, 'I': 9,
               'J': 3, 'K': 2, 'L': 2, 'M': 1, 'N': 0, 'O': 8, 'P': 9, 'Q': 8, 'R': 7,
               'S': 6, 'T': 5, 'U': 4, 'V': 3, 'W': 1, 'X': 3, 'Y': 2, 'Z': 0}

while True:                                 # 使用 while loop
    id_number = input('請輸入身分證字號: ')  # 輸入身分證字號
    if len(id_number) != 10: break          # 如果輸入的長度不等於 10 ，就跳出 while loop
    sex = int(id_number[1])                 # 取得第二碼數字
    if sex != 1 and sex != 2: break         # 第二碼如果不是 1 也不是 2 就跳出 while loop
    check_num = local_table[id_number[0]]   # 檢查數值最開始等於英文字母對照的數字
    # 依序檢查第二碼到第八碼
    for i in range(1, 9):
        check_num = check_num + int(id_number[i]) * (9 - i) # 根據公式計算
    check_num = check_num + int(id_number[9])   # 加入最後一碼的數值

    if check_num % 10 == 0:
        print('身分證字號正確')     # 如果除以十可以整除表示正確
    else:
        print('身分證字號格式錯誤')