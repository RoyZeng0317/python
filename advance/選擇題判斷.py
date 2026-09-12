questions = ["Which item would you like?", "2 + 2"]
options = [
    ["music", "book", "phone", "desktop"],
    ["4", "8", "1", "2"],
]
answers = ["desktop", "4"]

score = 0
for i, q in enumerate(questions):
    print(f"Question: {q}")
    for n, opt in enumerate(options[i], start=1):
        print(f"{n}. {opt}")

    choice = input("請輸入選項編號-> ")
    selected = options[i][int(choice) - 1]

    if selected == answers[i]:
        print("答對了!")
        score += 1
    else:
        print(f"答錯了，正確答案是: {answers[i]}")

print(f"總分: {score}/{len(questions)}")