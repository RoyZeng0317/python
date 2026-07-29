import tkinter as tk
import math
import random

寬, 高 = 900, 700
視角焦距 = 480
縮放 = 210
中心X, 中心Y = 寬 // 2, 高 // 2 + 20
背景色 = "#05070f"


def 建立羽球粒子():
    粒子 = []

    # 軟木頭：底部的實心圓球 (sphere-ish 隨機取點，模擬立體球面)
    軟木半徑 = 0.26
    軟木中心Y = -1.05
    for _ in range(150):
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(random.uniform(-0.2, 1))
        r = 軟木半徑 * (0.55 + 0.45 * random.random() ** 0.5)
        x = r * math.sin(phi) * math.cos(theta)
        z = r * math.sin(phi) * math.sin(theta)
        y = 軟木中心Y - r * math.cos(phi) * 0.85
        粒子.append([x, y, z, random.uniform(2.2, 3.4), "cork"])

    # 羽毛裙：16 根羽毛由窄底往上展開成喇叭狀，模擬真實羽球的重疊感
    羽毛數 = 16
    每根點數 = 42
    高度下, 高度上 = -0.82, 1.15
    半徑下, 半徑上 = 0.22, 1.0
    for f in range(羽毛數):
        基準角 = f / 羽毛數 * 2 * math.pi
        for i in range(每根點數):
            u = i / (每根點數 - 1)
            y = 高度下 + (高度上 - 高度下) * u
            半徑 = 半徑下 + (半徑上 - 半徑下) * (u ** 0.75)
            寬度 = (0.14 + 0.24 * u) * (random.random() - 0.5) * 2
            角度 = 基準角 + 寬度
            x = 半徑 * math.cos(角度)
            z = 半徑 * math.sin(角度)
            大小 = 1.5 + 2.6 * u
            粒子.append([x, y, z, 大小, "feather"])

    return 粒子


def 旋轉投影(粒子, 角Y, 角X):
    結果 = []
    cy, sy = math.cos(角Y), math.sin(角Y)
    cx, sx = math.cos(角X), math.sin(角X)
    for x, y, z, 大小, 群組 in 粒子:
        # 先繞 Y 軸旋轉(水平自轉)，再繞 X 軸做小幅擺動(增加立體感)
        x1 = x * cy - z * sy
        z1 = x * sy + z * cy
        y1 = y * cx - z1 * sx
        z2 = y * sx + z1 * cx

        深度 = z2 + 3.3
        if 深度 < 0.1:
            深度 = 0.1
        比例 = 視角焦距 / (視角焦距 + 深度 * 150)  # 透視：越遠越小

        sx2 = 中心X + x1 * 縮放 * 比例
        sy2 = 中心Y - y1 * 縮放 * 比例
        r = max(0.6, 大小 * 比例)
        結果.append((sx2, sy2, r, 深度, 群組))

    結果.sort(key=lambda p: -p[3])  # 由遠到近排序，畫家演算法避免遮擋錯誤
    return 結果


def 取色(群組, 深度):
    亮度 = max(0.32, min(1.0, 1.5 - 深度 / 6))
    if 群組 == "cork":
        r, g, b = 235, 190, 120
    else:
        r, g, b = 255, 255, 255
    r, g, b = int(r * 亮度), int(g * 亮度), int(b * 亮度)
    return f"#{r:02x}{g:02x}{b:02x}"


def 創建羽球():
    root = tk.Tk()
    root.title("羽球 3D 粒子效果")
    canvas = tk.Canvas(root, width=寬, height=高, bg=背景色, highlightthickness=0)
    canvas.pack()

    粒子 = 建立羽球粒子()
    狀態 = {"角Y": 0.0, "自轉速度": 0.02}

    def 結束(_=None):
        root.destroy()

    root.bind("<Escape>", 結束)
    root.bind("q", 結束)
    root.bind("<Left>", lambda e: 狀態.__setitem__("自轉速度", 狀態["自轉速度"] - 0.01))
    root.bind("<Right>", lambda e: 狀態.__setitem__("自轉速度", 狀態["自轉速度"] + 0.01))

    def 動畫():
        canvas.delete("all")
        狀態["角Y"] += 狀態["自轉速度"]
        角X = math.sin(狀態["角Y"] * 0.6) * 0.15

        for sx, sy, r, depth, group in 旋轉投影(粒子, 狀態["角Y"], 角X):
            canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill=取色(group, depth), outline="")

        root.after(16, 動畫)

    動畫()
    root.mainloop()


if __name__ == "__main__":
    創建羽球()
