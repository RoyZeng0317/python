def no_return():
    x = 1 + 1
    # No return
    return x

def get_name():
    return "Roy"

def get_list():
    return [1, 2, 3]

if __name__ == "__main__":
    results = no_return(), get_name(), get_list()
    print(results)