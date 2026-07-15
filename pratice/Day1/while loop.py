# while loop
print("班上五位同學的數學成績:")
i = 0
while i < 5:
    print("輸入第", i + 1, "位同學的數學成績:")
    score = int(input())
    print("第", i + 1, "位同學的數學成績為:", score)
    i += 1