import csv
import os

CSV_FILE = os.path.join(os.path.dirname(__file__), "檢定繳費.csv")

def load_data():
    data = []
    with open(CSV_FILE, encoding="cp950") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0:
                headers = row
            else:
                data.append(row)
    return headers, data

def save_data(headers, data):
    with open(CSV_FILE, "w", encoding="cp950", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

def show_all(data):
    print(f"{'序號':<4} {'學號':<8} {'費用':<6} {'繳費金額':<8} {'收據':<6} {'備註'}")
    print("=" * 50)
    for idx, row in enumerate(data, 1):
        sid, fee, paid, receipt, note = row[0], row[1], row[2] or "", row[3] or "", row[4] or ""
        status = "V" if paid else "X"
        print(f"{idx:<4} {sid:<8} {fee:<6} {paid:<8} {status:<6} {note}")

def record_payment(data):
    show_all(data)
    try:
        choice = int(input("\n請輸入要繳費的學生序號: "))
        if choice < 1 or choice > len(data):
            print("序號錯誤!")
            return
        row = data[choice - 1]
        amount = input(f"繳費金額 (預設 {row[1]}): ") or row[1]
        receipt = input("是否需要收據? (y/n): ").strip().lower()
        data[choice - 1][2] = amount
        data[choice - 1][3] = "是" if receipt == "y" else ""
        print(f"[OK] {row[0]} 繳費記錄完成!")
    except ValueError:
        print("輸入錯誤!")

def show_summary(data):
    total_fee = 0
    total_paid = 0
    paid_count = 0
    unpaid_count = 0
    for row in data:
        fee = int(row[1])
        total_fee += fee
        if row[2]:
            total_paid += int(row[2])
            paid_count += 1
        else:
            unpaid_count += 1
    print(f"\n{'='*30}")
    print(f"學生總數: {len(data)} 人")
    print(f"應收總額: {total_fee} 元")
    print(f"已繳人數: {paid_count} 人")
    print(f"未繳人數: {unpaid_count} 人")
    print(f"已收金額: {total_paid} 元")
    print(f"待收金額: {total_fee - total_paid} 元")
    print(f"收費進度: {total_paid / total_fee * 100:.1f}%")
    print(f"{'='*30}")

def main():
    headers, data = load_data()
    while True:
        print("\n=== 學生繳費管理系統 ===")
        print("1. 查看所有繳費狀況")
        print("2. 記錄繳費")
        print("3. 繳費統計摘要")
        print("4. 離開")
        choice = input("請選擇功能: ").strip()
        if choice == "1":
            show_all(data)
        elif choice == "2":
            record_payment(data)
            save_data(headers, data)
        elif choice == "3":
            show_summary(data)
        elif choice == "4":
            print("已儲存，離開系統!")
            break
        else:
            print("請輸入 1-4")

if __name__ == "__main__":
    main()
