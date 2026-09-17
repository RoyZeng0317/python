import turtle

多邊形 = 66 

colors = ['red', '#A349A4', 'lightblue', 'green', 'orange', 'yellow']
t = turtle.Pen()
turtle.bgcolor('black')

for x in range(120):
    t.pencolor(colors[x % 6])
    t.forward(x * 1.5)
    t.left(多邊形)  # 改變角度能畫出不同的幾何圖形
turtle.done()