def fib(n):
    if n > 1:
        return fib(n - 1) + fib(n - 2)
    return n
for i in range(20):
    print(fib(i), end = ',')