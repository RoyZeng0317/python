import random
num = random.randint(1, 100)
guess = int(input("Guess a number from 1 to 100: "))
while guess != num:
    if guess < num:
        print("So small!")
    else:
        print("So big!")
    guess = int(input("Try again: "))
print("Congrats! Guess right!")