import tkinter as tk, random, time, sys, math
h, a = [], []
t = ["多喝水", "好好愛自己", "好好吃飯", "保持好心情", "我想你了", "順順利利", "別熬夜", "天涼了多穿衣服"]
c = ["pink", "lightblue", "lightgreen", "lemonchiffon", "hotpink", "skyblue"]

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

def w():
    r = tk.Tk(); r.withdraw(); sw, sh = r.winfo_screenwidth(), r.winfo_screenheight(); n = 100
    for i, (x, y) in enumerate(g(n, sw, sh)):
        w = wx(x, y, "充實自己" if i == n - 1 else None); h.append(w); r.update(); time.sleep(0.03)
    time.sleep(1); [_.destroy() for _ in h if isinstance(_, tk.Toplevel) and _.winfo_exists()]
    for _ in range(sw // 150 * sh // 40 + 50):
        x, y = random.randint(0, sw - 150), random.randint(0, sh - 60)
        w = wx(x, y, is_h=False); a.append(w); r.update(); time.sleep(0.005)
    time.sleep(10); total_time = 1.0; num_windows = len(a)
    if num_windows> 0:
        interval = total_time / num_windows
        for window in a:
            if isinstance(window, tk.Toplevel) and window.winfo_exists(): window.destroy()
            r.update(); time.sleep(interval)
    r.mainloop()

if __name__ == "__main__": w()