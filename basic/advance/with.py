import os, sys

with open(os.path.join(sys.path[0], "data.txt"), "r") as f:
    data = f.read()
    print(data)

