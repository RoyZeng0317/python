import random
a = []
group = int(input("請輸入需要產生出的組數: "))
for i in range(group):
    a = []
    while len(a) < 6:
        b = random.randint(1, 50)
        if b not in a:
            a.append(b)
    print(a)