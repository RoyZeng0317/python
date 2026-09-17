arr = [5, 3, 8, 4, 2]
n = 5
temp = 0
for i in range(0, n - 1):
    for j in range(0, n - 1):
        if arr[j] > arr[j + 1]:
            print(arr)
            temp = arr[j]
            print(temp)
            arr[j] = arr[j + 1]
            print(arr)
            arr[j + 1] = temp
print(arr)