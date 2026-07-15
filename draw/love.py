import random
import time
from math import sin, cos, pi, log
import tkinter as tk

canvas_width = 640 # the paper width
canvas_height = 480 # the paper height
canvas_center_x = canvas_width / 2 # paper center of x asix
canvas_center_y = canvas_height / 2 # paper center of y asix
img_enlager = 11 # zoom it change at here.
heart_color = "#e86184" # heart color

windows_titile = 'Heart' # window title
heart_center_text = ''
heart_center_text_color = '#e86184'

window = tk.Tk()
window.title("跳動的愛心")
window.geometry("800x600")

canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg='white')
canvas.pack()

def heart_function(t):
    x = 16 * sin(t) ** 3
    y = 13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t)
    return x, y
t = 0
while t < 2 * pi:
    x, y = heart_function(t)
    x = canvas_center_x + x * img_enlager
    y = canvas_center_y - y * img_enlager
    canvas.create_oval(x, y, x + 1, y + 1, fill=heart_color, outline=heart_color)
    t += 0.01
    window.update()
    time.sleep(0.01)

# 畫面要一直顯示，不打就會閃一下
window.mainloop()