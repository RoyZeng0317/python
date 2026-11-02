fruits = ["Apple", "Banana", "Orange"]
# enumerate(iterable, start=0)

# for fruit in fruits:
#     print(fruit)
# for idx, fruit in enumerate(fruits):
#     print(idx, fruit)

# a = list(enumerate(["A", "B", "C"]))
# print(a)

# names = ["Roy", "Daniel", "Joy"]

# for i, name in enumerate(names):
#     print(i + 1, name)

# numbers = [10, 20, 30]
# for i, num in enumerate(numbers, start=1):
#     print(i + num)

scores = [50, 80, 65, 90]

for idx, score in enumerate(scores, start=1):
    if idx % 2 == 0 and score >= 70:
        print(idx, score)
