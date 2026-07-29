# list 修改
# fruits = ["watermelon", "pineapple", "dragon fruit"]

# print(fruits[0])
# fruits[1] = "grapes"
# fruits.append("banana")
# print(fruits)
# for fruit in fruits:
#     print(fruit)
# list 的另項新增
# usr = {"name": "Daniel", "age":18}
# print(usr["name"]) # 輸出 usr list 裡的 name value
# usr["age"] = 24 # 修改 age 為 24
# usr["gender"] = "male" # 加上了 gender value is male
# print(usr) # 輸出 usr list
# 重複索引
# num = {1, 2, 2, 3, 3, 3}
# print(len(num))
# num.add(4)
# num.add(2)
# print(len(num))

# num = [10, 20, 30, 40, 50]
# print(num[-1]) # 指最後一個
# print(num[1:4]) # idx 從零開始數 1 - 4
# squares = [x * x for x in range(1, 6)] list 中有 1-5 每個都平方
# print(squares)

usr = {"name": "daniel", "age": 24, "gender": "male"}
print(usr.get("score", 0)) # 沒有則輸出 0 表 False
usr.update({"age": 20, "level": "入門"})
print(usr.items())