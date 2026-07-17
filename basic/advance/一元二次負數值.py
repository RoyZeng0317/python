import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(-10, 10, 100)
y = x ** 2 + x + 1

plt.plot(x, y)
# 顯示座標名稱
plt.xlabel("x")
plt.ylabel("y")
# 顯示標題
plt.title("y = x ^ 2 + x + 1")
# 顯示網格
plt.grid(True)
# 顯示圖表
plt.show()