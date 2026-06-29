path = "C:\\Users\\Roy\\Documents\\GitHub\\python\\AI\\week1\\Day3\\52de6007-a837-4827-81b4-dc061e8fee0c.csv"
f = open(path, 'r', newline='', encoding='utf-8')
a = f.read()
# print(a) # 先查看檔案原始內容是啥
# print(type(a)) # 再查看他類型是什麼
# print(len(a)) # 看有多長
b = a.split("\n") # 決定用\n作為分割的依據
# print(b) # 看一下分割完的內容
# print(type(b))
# print(len(b)) # 比對完前三筆是我要的
# print(b[0]) # 查看總體的數量(列數)
# print(b[1])
# print(b[2])
# print(b[3])
# print(b[4])
# print(len(b[3]))
c = [] # 把每一列的每一行單獨存成 list
for i in range(len(b)): # 處理每一行
    c.append(str(b[i]).split(",")) # 把每行的數值換成 str 透過 spilt 把,分割為
    if(i < 40):
        print(c[i][8])
