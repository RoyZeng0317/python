import math
import tkinter as tk
from tkinter import ttk, messagebox


def get_value(entry: ttk.Entry):
    text = entry.get().strip()
    return float(text) if text else None


def set_value(entry: ttk.Entry, value: float):
    entry.delete(0, tk.END)
    entry.insert(0, f"{value:.6g}")


def make_field(frame, row, label_text):
    ttk.Label(frame, text=label_text).grid(row=row, column=0, sticky="w", padx=8, pady=6)
    entry = ttk.Entry(frame, width=18)
    entry.grid(row=row, column=1, padx=8, pady=6)
    return entry


def make_clear_button(frame, row, entries):
    def clear():
        for entry in entries:
            entry.delete(0, tk.END)

    ttk.Button(frame, text="清除", command=clear).grid(row=row, column=1, sticky="e", padx=8, pady=10)


# ---------- 歐姆定律 V = I * R ----------
def build_ohm_tab(notebook):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="歐姆定律")

    v_entry = make_field(frame, 0, "電壓 V (V)")
    i_entry = make_field(frame, 1, "電流 I (A)")
    r_entry = make_field(frame, 2, "電阻 R (Ω)")

    def calculate():
        V, I, R = get_value(v_entry), get_value(i_entry), get_value(r_entry)
        blanks = [name for name, val in (("V", V), ("I", I), ("R", R)) if val is None]

        if len(blanks) != 1:
            messagebox.showwarning("輸入錯誤", "請恰好留一格空白，讓程式計算該數值。")
            return

        try:
            if blanks[0] == "V":
                set_value(v_entry, I * R)
            elif blanks[0] == "I":
                set_value(i_entry, V / R)
            else:
                set_value(r_entry, V / I)
        except ZeroDivisionError:
            messagebox.showerror("計算錯誤", "除數不可為 0。")

    ttk.Button(frame, text="計算", command=calculate).grid(row=3, column=0, padx=8, pady=10)
    make_clear_button(frame, 3, [v_entry, i_entry, r_entry])
    return frame


# ---------- 電功率 P = V * I ----------
def build_power_tab(notebook):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="電功率")

    p_entry = make_field(frame, 0, "功率 P (W)")
    v_entry = make_field(frame, 1, "電壓 V (V)")
    i_entry = make_field(frame, 2, "電流 I (A)")

    def calculate():
        P, V, I = get_value(p_entry), get_value(v_entry), get_value(i_entry)
        blanks = [name for name, val in (("P", P), ("V", V), ("I", I)) if val is None]

        if len(blanks) != 1:
            messagebox.showwarning("輸入錯誤", "請恰好留一格空白，讓程式計算該數值。")
            return

        try:
            if blanks[0] == "P":
                set_value(p_entry, V * I)
            elif blanks[0] == "V":
                set_value(v_entry, P / I)
            else:
                set_value(i_entry, P / V)
        except ZeroDivisionError:
            messagebox.showerror("計算錯誤", "除數不可為 0。")

    ttk.Button(frame, text="計算", command=calculate).grid(row=3, column=0, padx=8, pady=10)
    make_clear_button(frame, 3, [p_entry, v_entry, i_entry])
    return frame


# ---------- 庫侖定律 Q = C * V ----------
def build_coulomb_tab(notebook):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="庫侖定律")

    q_entry = make_field(frame, 0, "電荷 Q (C)")
    c_entry = make_field(frame, 1, "電容 C (F)")
    v_entry = make_field(frame, 2, "電壓 V (V)")

    def calculate():
        Q, C, V = get_value(q_entry), get_value(c_entry), get_value(v_entry)
        blanks = [name for name, val in (("Q", Q), ("C", C), ("V", V)) if val is None]

        if len(blanks) != 1:
            messagebox.showwarning("輸入錯誤", "請恰好留一格空白，讓程式計算該數值。")
            return

        try:
            if blanks[0] == "Q":
                set_value(q_entry, C * V)
            elif blanks[0] == "C":
                set_value(c_entry, Q / V)
            else:
                set_value(v_entry, Q / C)
        except ZeroDivisionError:
            messagebox.showerror("計算錯誤", "除數不可為 0。")

    ttk.Button(frame, text="計算", command=calculate).grid(row=3, column=0, padx=8, pady=10)
    make_clear_button(frame, 3, [q_entry, c_entry, v_entry])
    return frame


# ---------- 交流電路阻抗 ----------
def build_ac_tab(notebook):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text="交流電路")

    f_entry = make_field(frame, 0, "頻率 f (Hz)")
    l_entry = make_field(frame, 1, "電感 L (H)")
    c_entry = make_field(frame, 2, "電容 C (F)")
    xl_entry = make_field(frame, 3, "電感阻抗 XL (Ω)")
    xc_entry = make_field(frame, 4, "電容阻抗 XC (Ω)")

    def calculate():
        f, L, C = get_value(f_entry), get_value(l_entry), get_value(c_entry)

        if f is None or L is None or C is None:
            messagebox.showwarning("輸入錯誤", "請輸入頻率 f、電感 L、電容 C 三個數值。")
            return

        try:
            omega = 2 * math.pi * f
            set_value(xl_entry, omega * L)
            set_value(xc_entry, 1 / (omega * C))
        except ZeroDivisionError:
            messagebox.showerror("計算錯誤", "除數不可為 0。")

    ttk.Button(frame, text="計算", command=calculate).grid(row=5, column=0, padx=8, pady=10)
    make_clear_button(frame, 5, [f_entry, l_entry, c_entry, xl_entry, xc_entry])
    return frame


def main():
    root = tk.Tk()
    root.title("基本電學計算機")
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    build_ohm_tab(notebook)
    build_power_tab(notebook)
    build_coulomb_tab(notebook)
    build_ac_tab(notebook)

    root.mainloop()


if __name__ == "__main__":
    main()
