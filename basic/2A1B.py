import random


def generate_secret():
    """產生4個不重複數字的答案"""
    digits = list("0123456789")
    random.shuffle(digits)
    return digits[:4]


def check(secret, guess):
    """回傳 (A的數量, B的數量)"""
    a = sum(1 for i in range(4) if secret[i] == guess[i])
    b = sum(1 for d in guess if d in secret) - a
    return a, b


def main():
    secret = generate_secret()
    print("=== 2A1B 猜數字遊戲 ===")
    print("請猜出4個不重複的數字（0~9），位置對且數字對得A，數字對但位置錯得B")

    attempts = 0
    while True:
        guess = input("請輸入四位數字--> ").strip()

        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            print("輸入錯誤！請輸入4個「不重複」的數字（例如 1234）")
            continue

        attempts += 1
        a, b = check(secret, list(guess))

        if a == 4:
            print(f"恭喜猜對了！答案是 {''.join(secret)}，共猜了 {attempts} 次")
            break

        print(f"{a}A{b}B")


if __name__ == "__main__":
    main()
