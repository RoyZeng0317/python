"""計算機：基本四則運算 + 匯率換算 + 電阻/電容數值換算 + 電學公式（歐姆定律）+ 股票損益。

基本四則運算留在這支檔案，其餘每項功能各自獨立一支檔案（匯率.py、電阻電容.py、
歐姆.py、股票.py），各自可被這支檔案當分頁掛載，也能單獨執行。
"""

import tkinter as tk
from tkinter import messagebox, ttk

import 股票
import 匯率
import 電阻電容
import 歐姆
from lib import basic_calc

BG_COLOR = "#1e1e1e"
PANEL_BG = "#252526"
KEY_BG = "#2d2d2d"
KEY_FG = "#ffffff"
KEY_ACTIVE_BG = "#3d3d3d"
ACCENT_BG = "#0e639c"
ACCENT_ACTIVE_BG = "#1177bb"
KEY_FONT = ("Segoe UI", 16, "bold")
DISPLAY_FONT = ("Segoe UI", 28, "bold")
LABEL_FONT = ("Segoe UI", 11)


class BasicCalculatorTab(ttk.Frame):
    """基本四則運算分頁。"""

    KEYS = (
        ("C", "action"), ("⌫", "action"), ("±", "action"), ("/", "op"),
        ("7", "digit"), ("8", "digit"), ("9", "digit"), ("*", "op"),
        ("4", "digit"), ("5", "digit"), ("6", "digit"), ("-", "op"),
        ("1", "digit"), ("2", "digit"), ("3", "digit"), ("+", "op"),
        ("0", "digit"), (".", "digit"), ("=", "equals"),
    )

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=16)
        self.engine = basic_calc.CalculatorEngine()

        self.display_var = tk.StringVar(value="0")
        display = tk.Label(
            self, textvariable=self.display_var, font=DISPLAY_FONT,
            bg=BG_COLOR, fg=KEY_FG, anchor="e", padx=12, pady=16,
        )
        display.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))

        grid_frame = tk.Frame(self, bg=PANEL_BG)
        grid_frame.grid(row=1, column=0, columnspan=4, sticky="nsew")
        for i in range(4):
            grid_frame.columnconfigure(i, weight=1)

        row = col = 0
        for label, kind in self.KEYS:
            span = 2 if label == "0" else 1
            is_accent = kind in ("op", "equals")
            btn = tk.Button(
                grid_frame, text=label, width=4, height=2, font=KEY_FONT,
                bg=ACCENT_BG if is_accent else KEY_BG, fg=KEY_FG,
                activebackground=ACCENT_ACTIVE_BG if is_accent else KEY_ACTIVE_BG,
                activeforeground=KEY_FG, relief="flat", bd=0,
                command=lambda l=label, k=kind: self.handle_press(l, k),
            )
            btn.grid(row=row, column=col, columnspan=span, padx=4, pady=4, sticky="nsew")
            col += span
            if col >= 4:
                col = 0
                row += 1

    def handle_press(self, label: str, kind: str) -> None:
        if kind == "digit":
            if label == ".":
                self.engine.input_decimal_point()
            else:
                self.engine.input_digit(label)
        elif kind == "op":
            self.engine.input_operator(label)
        elif kind == "equals":
            try:
                self.engine.equals()
            except ZeroDivisionError as exc:
                messagebox.showerror("錯誤", str(exc))
                self.engine.reset()
        elif kind == "action":
            if label == "C":
                self.engine.reset()
            elif label == "⌫":
                self.engine.backspace()
            elif label == "±":
                self.engine.toggle_sign()
        self.display_var.set(self.engine.display)


class CalculatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("計算機")
        self.configure(bg=BG_COLOR)
        self.geometry("560x640")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 11))
        style.configure("TFrame", background=PANEL_BG)
        style.configure("TLabel", background=PANEL_BG, foreground=KEY_FG, font=LABEL_FONT)
        style.configure("TButton", font=("Segoe UI", 10))

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        notebook.add(BasicCalculatorTab(notebook), text="基本計算機")
        notebook.add(匯率.CurrencyTab(notebook), text="匯率換算")
        notebook.add(電阻電容.ResistorCapacitorTab(notebook), text="電阻/電容")
        notebook.add(歐姆.OhmLawTab(notebook), text="電學公式")
        notebook.add(股票.build_stock_frame(notebook, show_title=False), text="股票損益")


def main() -> None:
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
