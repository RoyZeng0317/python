# 假病毒
import tkinter as tk
from tkinter import messagebox
root = tk.Tk()
root.withdraw()
while True:
    messagebox.showinfo("提示", "系統將關機")
root.destroy()