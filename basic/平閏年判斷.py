# 平閏年判斷
years = int(input("請輸入欲查詢的平閏年: "))
if (years % 4 == 0 and years % 100 != 0) or years % 400 == 0:
    print(f"{years} 為閏年")
else:
    print(f"{years} 為平年")