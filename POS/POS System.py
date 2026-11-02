def main():
    print("=== 超商結帳系統 ===")
    print("=== 請輸入收銀員編號及密碼 ===")
    ac = input("員工編號: ")
    pwd = input("密碼: ")
    # input() 回傳的是字串，所以要跟字串 "999" 比較
    while ac != "999" or pwd != "999":
        print("帳號或密碼錯誤，請重新輸入\n")
        ac = input("員工編號: ")
        pwd = input("密碼: ")
    print("歡迎進入收銀員系統~~^_^~~\n")

    fun = ["結帳機台", "中獎發票兌換", "卡片交易", "庫存查詢"]
    for i, name in enumerate(fun, start=1):
        print(f"{i}. {name}")
    choice = input("請選擇功能: ")


if __name__ == "__main__":
    main()
