def main():
    y = int(input("請輸入要判斷的西元年: "))
    if y % 4 == 0:
        print(f"{y} 是閏年!")
    else:
        print(f"{y} 不是閏年!")
        
if __name__ == "__main__":
    main()