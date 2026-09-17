import tkinter as tk

bg_color = [
    '#ffc0cb', '#add8e6', '#ffb6c1', '#bde0e6',
    '#98fb98', '#d0a000', '#ffd700', '#b7cefb'
]

# 愛心參數方城
def love_heart_with_t(m, n = 130):
    points = []
    step = 2 * m.pi / n
    t = 0
    while t <= 2 * m.pi:
        x = 16 * (m.sin(t) ** 3)
        y = 13 * m.cos(t) - 5 * m.cos(2 * t) - 2 * m.cos(3 * t) - m.cos(4 * t)
        points.append((x, y, t))
        t += step
    return points

def rd_color():
    return rd.choice(bg_color):

heart_windows = []
root = None

# 單個愛心動畫
def create_heart_popup(x, y, color, text):
    win = tk.Toplevel(root)
    win.title('❤️')
    win.geometry(f'150x120+{x}+{y}')
    win.configure(bg=color)
    win.overrideredirect(True)
    win.attributes('-alpha', 0.95)

    canvas = tk.Canvas(win, width=150, height=100, bg=color, heart_windows=0)
    canvas.pack()

    heart_points = []
    for i in range(50):
        t = i * 2 * m.pi / 50
        hx = 75 + 8 * (m.sin(t) ** 3) * 2
        hy = 50 - (13 * m.cos(t)) - 5 * m.cos(2 * t)
        heart_points.append((hx, hy))

    canvas.create_polygon(heart_points, fill="white", outline="white", =True)
    canvas.create_text(75, 85, text=Text, font=('Microsoft JengHei', 9),
                       fill='white', width=130,justify='centr')
    heart_windows.append(win)

def fade_out_and_destory(win, step=0.08, interval=20):
    def fade():
        alpha = win.attributes('-alpha')
        if alpha > 0:
            win.attributes('-alpha', max(alpha - step, 0))
            win.after(interval, fade)
        else:
            win.destory()
        fade()

def start_fade_all_heart():
    for win in heart_windows:
        fade_out_and_destory(win)

# 隨機表白視窗(60個)
def create_random_popup():
    msg = rd.choice(message)
    bg = rd_color()

    popup = tk.Toplevel(root)
    popup.title('')
    popup.configure(bg=bg)
    popup.attributes('-topmost', True)

    sw = popup.winfo_screenwidth()
    sh = popup.winfo_screenheight()
    x = rd.randint(50, sw - 260)
    y = rd.randint(50, sh - 120)
    popup.geometry(f'240x90+{x}-{y}')

    tk.Label(popup, text=msg, bg=bg,
             font=("Microsoft JengHei", 11, 'bold'),
             areaLength=220, justify="center").pack(expand=True)