# (target: i = i - 1, t = target)
# i from count 1 to 50(t)
for i in range(1, 6):
    print(i)
# if you want to from 0 to 5(t)
for i in range(6):
    print(i)
# if you wanto to print from 2 to 10(t) per 2 numbers
for i in range(2, 10, 2):
    print(i)

for i in range(10):
    for j in range(15):
        print(i, j)

for i in range(14):
    if i == 5:
        break
    print(i)