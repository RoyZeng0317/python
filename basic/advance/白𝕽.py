import tkinter as tk, random, time, sys, math

h, a = [], []
t = [""]
c = [""]

def g(n, w, h):
    p = []
    for i in range(n):
        th = i / n * 2 * math.pi
        x = 16 * math.sin(th) ** 3; y = 13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th)
        sx = int(w / 2 + x * 20 - 50); sy = int(h / 2 - y * 20 - 80)
        p.append((max(0, min(sx, w - 150)), max(0, min(sy, h - 60))))
    return p

def wx(x, y, tip=None, is_h = True):
    w = tk.Toplevel()
    w.geometry(f"150x60+{x}+{y}"); w.title("提示"); w.attributes('-topmost', 1)
    tk.Label(w, text=tip or random.choice(t), bg=random.choice(c), font=("Microsoft JengHei", 14), width=20, height=3).pack()
    w.bind('<space>', lambda e: [_.destroy() for _ in h + a] or sys.exit())
    return w
