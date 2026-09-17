import tkinter as tk
from datetime import datetime

win = tk.Tk()
win.title("Current Time")

(label := tk.Label(win, font=("Arial", 24))).pack(padx=20, pady=20)

def main():
    now = datetime.now()
    label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    win.after(1000, main)

main()
win.mainloop()