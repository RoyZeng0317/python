"""
let the user to enter the password, and to verify the password
only can use the three times to verify, under the three times can't login.
assume the current password is 3388
"""

pwd = 3388
i = 1

while i <= 3:
    new_pw = int(input("Please enter the password:"))
    if new_pw != pwd:
        print("The password is wrong!!!")
        i = i + 1
        continue
    else:
        print("The passsword is correct!!!")
        break
if i > 3:
    print("The password are wrong three times, cancel to login!!\n")
    