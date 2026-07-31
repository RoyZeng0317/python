import matplotlib.pyplot as plt
import numpy as np

# xpoints = np.array([0, 6])
# ypoints = np.array([0, 100])

# plt.plot() 常見呼叫方式(matplotlib 官方文件示範，此處僅作說明，不執行):
# plt.plot(x, y)         畫出 x, y 兩軸資料，預設樣式
# plt.plot(x, y, 'bo')   'bo' = 藍色圓點
# plt.plot(y)            只給 y，x 軸自動用索引 0..N-1
# plt.plot(y, 'r+')      'r+' = 紅色十字
# 基本畫線
# 一般實線
# xpoints = np.array([1, 8])
ypoints = np.array([3, 10])
# 不規則實線
# xpoints = np.array([1, 2, 6, 8])
# ypoints = np.array([3, 8, 1, 10])
ypoints = np.array([3, 8, 1, 10, 5, 7])
# plt.plot(xpoints, ypoints)    # 繪製長線
# plt.plot(xpoints, ypoints, 'o') # 繪製圓點
plt.plot(ypoints)   # 不指定 x 軸


plt.show()