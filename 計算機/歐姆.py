"""電學公式（歐姆定律）：V、I、R、P 任意輸入兩個已知量，自動算出其餘。

計算邏輯放在 lib/ohm.py（不依賴 tkinter），這支檔案只負責畫面與事件處理，
可被 計算機.py 當分頁掛載，也能單獨執行。
"""

import tkinter as tk
from tkinter import messagebox, ttk

from lib import basic_calc, ohm


class OhmLawTab(ttk.Frame):
    """電學公式分頁：V、I、R、P 任意輸入兩個已知量，自動算出其餘。"""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=16)
        ttk.Label(
            self, text="輸入任意兩個已知量，其餘會自動算出（V=IR，P=VI=I²R=V²/R）",
            font=("Segoe UI", 12, "bold"), wraplength=420,
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        self.vars: dict[str, tk.StringVar] = {}
        rows = (
            ("V", "電壓 V（伏特）"),
            ("I", "電流 I（安培）"),
            ("R", "電阻 R（歐姆）"),
            ("P", "功率 P（瓦特）"),
        )
        for i, (key, label) in enumerate(rows, start=1):
            ttk.Label(self, text=label).grid(row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            ttk.Entry(self, textvariable=var, width=16).grid(row=i, column=1, sticky="w", pady=6, padx=8)
            self.vars[key] = var

        button_row = ttk.Frame(self)
        button_row.grid(row=5, column=0, columnspan=2, sticky="w", pady=12)
        ttk.Button(button_row, text="計算", command=self.on_solve).pack(side="left")
        ttk.Button(button_row, text="清除", command=self.on_clear).pack(side="left", padx=8)

        self.result_var = tk.StringVar(value="")
        ttk.Label(self, textvariable=self.result_var, foreground="#4caf50").grid(
            row=6, column=0, columnspan=2, sticky="w"
        )

    def on_solve(self) -> None:
        parsed: dict[str, float | None] = {}
        for key, var in self.vars.items():
            text = var.get().strip()
            if text == "":
                parsed[key] = None
                continue
            try:
                parsed[key] = float(text)
            except ValueError:
                messagebox.showerror("輸入錯誤", f"{key} 請輸入數字")
                return
        try:
            result = ohm.solve(**parsed)
        except ohm.OhmLawError as exc:
            messagebox.showerror("無法計算", str(exc))
            return
        for key, value in result.items():
            self.vars[key].set(basic_calc.format_number(value))
        self.result_var.set("計算完成")

    def on_clear(self) -> None:
        for var in self.vars.values():
            var.set("")
        self.result_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("電學公式")
    OhmLawTab(root).pack(fill="both", expand=True)
    root.mainloop()
