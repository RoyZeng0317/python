def only_5():
   # only continue the 5
    for a in range(0, 10, 1):
        if a == 3:
            continue
        print(a, end=" ")

def main():
    # partice the continue
    for a in range(10):
        for b in range(a + 1):
            if b == 6:
                continue
            print("%d", "%b, end=")
    print()