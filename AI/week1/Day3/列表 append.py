import math
import matplotlib.pyplot as plt

x = []
y = []
z = []
for i in range (50):
    x.append(i + 1)
    y.append(math.pow(i + 1, 2)+ (i + 1) + 1)
    z.append(math.pow(i + 1, 2) + (i + 1) + 1)
    print(y)

plt.plot(x, y)

plt.show()