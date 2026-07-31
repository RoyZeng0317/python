"""匯率換算：即時連網抓取匯率，抓取失敗時可改用手動輸入匯率。

換算邏輯放在 lib/currency.py（不依賴 tkinter），這支檔案只負責畫面與事件處理，
可被 計算機.py 當分頁掛載，也能單獨執行。
"""

import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from lib import currency


class CurrencyTab(ttk.Frame):
    """匯率換算分頁：即時連網抓取，抓取失敗時可改用手動輸入匯率。"""

    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=16)
        self.columnconfigure(1, weight=1)
        codes = list(currency.CURRENCY_NAMES.keys())

        ttk.Label(self, text="金額").grid(row=0, column=0, sticky="w", pady=6)
        self.amount_var = tk.StringVar(value="100")
        ttk.Entry(self, textvariable=self.amount_var).grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(self, text="從").grid(row=1, column=0, sticky="w", pady=6)
        self.from_var = tk.StringVar(value="USD")
        ttk.Combobox(self, textvariable=self.from_var, values=codes, state="readonly").grid(
            row=1, column=1, sticky="ew", pady=6
        )

        ttk.Label(self, text="到").grid(row=2, column=0, sticky="w", pady=6)
        self.to_var = tk.StringVar(value="TWD")
        ttk.Combobox(self, textvariable=self.to_var, values=codes, state="readonly").grid(
            row=2, column=1, sticky="ew", pady=6
        )

        self.convert_btn = ttk.Button(self, text="即時換算", command=self.on_convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 4))

        self.status_var = tk.StringVar(value="尚未查詢")
        ttk.Label(self, textvariable=self.status_var, foreground="#9aa0a6").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )

        self.result_var = tk.StringVar(value="—")
        ttk.Label(self, textvariable=self.result_var, font=("Segoe UI", 18, "bold")).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(10, 16)
        )

        # 即時抓取失敗時才顯示的手動輸入匯率區塊
        self.manual_frame = ttk.Frame(self)
        ttk.Label(self.manual_frame, text="連線失敗，請手動輸入匯率（1 從幣 = ? 到幣）：").pack(anchor="w")
        manual_row = ttk.Frame(self.manual_frame)
        manual_row.pack(fill="x", pady=4)
        self.manual_rate_var = tk.StringVar()
        ttk.Entry(manual_row, textvariable=self.manual_rate_var, width=12).pack(side="left")
        ttk.Button(manual_row, text="用手動匯率計算", command=self.on_manual_convert).pack(side="left", padx=6)

    def on_convert(self) -> None:
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入正確的金額數字")
            return

        self.status_var.set("查詢中…")
        self.convert_btn.state(["disabled"])
        self.manual_frame.grid_forget()
        from_code, to_code = self.from_var.get(), self.to_var.get()

        def worker() -> None:
            try:
                result = currency.convert(amount, from_code, to_code)
                ts = currency.last_updated(from_code)
            except currency.ExchangeRateError as exc:
                self.after(0, lambda: self.on_failure(str(exc)))
                return
            self.after(0, lambda: self.on_success(amount, from_code, to_code, result, ts))

        threading.Thread(target=worker, daemon=True).start()

    def on_success(self, amount: float, from_code: str, to_code: str, result: float, ts) -> None:
        text = time.strftime("%H:%M:%S", time.localtime(ts)) if ts else "—"
        self.status_var.set(f"即時匯率查詢成功（更新時間 {text}）")
        self.result_var.set(f"{amount:g} {from_code} = {result:.4f} {to_code}")
        self.convert_btn.state(["!disabled"])

    def on_failure(self, message: str) -> None:
        self.status_var.set("即時匯率抓取失敗，請改用下方手動輸入")
        self.convert_btn.state(["!disabled"])
        self.manual_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(4, 0))

    def on_manual_convert(self) -> None:
        try:
            amount = float(self.amount_var.get())
            rate = float(self.manual_rate_var.get())
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入正確的金額與匯率數字")
            return
        result = currency.manual_convert(amount, rate)
        self.result_var.set(f"{amount:g} {self.from_var.get()} = {result:.4f} {self.to_var.get()}（手動匯率）")
        self.status_var.set("使用手動輸入匯率計算")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("匯率換算")
    CurrencyTab(root).pack(fill="both", expand=True)
    root.mainloop()
