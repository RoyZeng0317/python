# for i in range(10):
#     if i == 3 or i == 5:
#         continue
#     print(i)

# levels = [1, 2, 3, 4, "隱藏關卡", 6, 7, 8]

# for level in levels:
#     if level == "隱藏關卡":
#         print(f"第{level}打不過，跳過!")
#         continue
#     print(f"正在挑戰第{level}關")
# print("遊戲通關!")

# tasks = [
#     ["打小怪", 30], ["收集飽食", 80],
#     ["打贏 boss", 120], ["送信", 20],
#     ["完成成就", 100]
# ]
# for task in tasks:
#     name = task[0]
#     reward = task[1]
#     if reward <= 50:
#         print(f"{name}獎勵{reward}太低跳過不做")
#         continue
#     print(f"完成任務{name}獲得{reward}金幣")

# names = ["bob", "jack", "", "cindy", "lucy", ""]

# for name in names:
#     if not name:
#         continue
#     print(name)

# numbers = [1, 2, 5, 7, 13, 21, 85, 99, 123, 175]
# for n in numbers:
#     if n == 0:
#         continue
#     print(100 / n)

def is_valid(item):
    return item != ""

items = ["watermelon", "banana", "apple", "dragonfruit", ""]
for item in items:
    if not is_valid(item):
        continue
    print(item)