# for loop
for i in range(5):
    print(i)

print("班上五位同學的數學成績:")
for i in range(5):
    print("請輸入第", i + 1, "位同學的數學成績:")
    
    score = int(input())
    print("第", i + 1, "位同學的數學成績為:", score)