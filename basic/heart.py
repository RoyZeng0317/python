# 匯入繪製庫
import turtle
# 建立視窗
screen = turtle.Screen()
# 視窗背景色為黑色
screen.bgcolor("#111827")
# 建立一支筆
pen = turtle.Turtle()
# 筆的顏色為紅色
pen.color("#ff4d6d")
# 匯出圖形填充顏色為紅色
pen.fillcolor("#ff4d6d")
# 筆的大小為 3
pen.pensize(3)
# 速度為 8
pen.speed(8)
# 開始填充
pen.begin_fill()
# 從往左側開始 140 度畫一條斜邊
pen.left(140)
# 向前畫180
pen.forward(180)
# 重複執行 200 次
for _ in range(200):
    # 向右轉 1 步
    pen.right(1)
    # 同時向前走 1.5 步
    pen.forward(1.5)
# 再次向左走 120 的一條斜邊
pen.left(120)
# 同上再次重複200次
for _ in range(200):
    pen.right(1)
    pen.forward(1.5)
# 走回到第180度的位置
pen.forward(180)
# 結束並填充 
pen.end_fill()
# 隱藏比筆
pen.hideturtle()
# 結束執行
turtle.done()