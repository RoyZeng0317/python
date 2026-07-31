"""股票損益試算：輸入股票代號自動抓即時現價，算出買入後的報酬。

抓取邏輯放在 lib/stock.py（不依賴 tkinter），這支檔案只負責畫面與事件處理。
"""

import tkinter as tk
from tkinter import messagebox

from lib.stock import StockPriceError, fetch_price, profit

FIELDS = ("股票代號", "買入價位", "股數", "現價")
_DECIMAL_ALIASES = str.maketrans("，。,", "...")  # NumLock 關閉/中文輸入法可能打出全形句點或逗號，一律當小數點


def _to_float(text: str) -> float:
    """把全形句點「。」或逗號「，/,」正規化成半形句點再轉 float。"""
    return float(text.strip().translate(_DECIMAL_ALIASES))


def _bind_numpad_decimal(entry: tk.Entry) -> None:
    """有些鍵盤（NumLock 關閉、或獨立小鍵盤）小數點鍵送出的 keysym 跟 Delete
    鍵完全相同，Tk 因此誤判成刪除鍵；但 event.char 仍然是 '.'（真的 Delete
    鍵這裡會是空字串），用這點分辨並手動插入小數點。"""

    def insert_dot(_event: tk.Event) -> str:
        entry.insert(tk.INSERT, ".")
        return "break"

    def on_delete(event: tk.Event):
        return insert_dot(event) if event.char == "." else None  # 空字串才是真正的 Delete 鍵

    entry.bind("<KP_Decimal>", insert_dot)
    entry.bind("<KP_Separator>", insert_dot)
    entry.bind("<Delete>", on_delete)


def build_stock_frame(parent: tk.Misc, *, show_title: bool = True) -> tk.Frame:
    """建立股票損益試算的操作介面，獨立視窗（build_ui）與其他視窗（如 計算機.py）都掛這個 frame，避免同一份邏輯複製兩份。"""
    frame = tk.Frame(parent)

    entries = {}
    for row, label in enumerate(FIELDS):
        tk.Label(frame, text=label).grid(row=row, column=0, padx=8, pady=6, sticky="e")
        entry = tk.Entry(frame)
        entry.grid(row=row, column=1, padx=8, pady=6)
        entries[label] = entry
        if label in ("買入價位", "現價"):
            _bind_numpad_decimal(entry)

    result_var = tk.StringVar(value="報酬: -")
    tk.Label(frame, textvariable=result_var, font=("Arial", 12, "bold")).grid(
        row=len(FIELDS), column=0, columnspan=2, pady=10
    )

    def on_fetch(_event=None):
        code = entries["股票代號"].get().strip()
        if not code:
            messagebox.showerror("錯誤", "請輸入股票代號")
            return
        try:
            price, name = fetch_price(code)
        except StockPriceError as exc:
            messagebox.showerror("現價抓取失敗", f"{exc}\n請自行於「現價」欄位手動輸入")
            return
        entries["現價"].delete(0, tk.END)
        entries["現價"].insert(0, str(price))
        if show_title:
            frame.winfo_toplevel().title(f"股票損益試算 - {name}")

    entries["股票代號"].bind("<Return>", on_fetch)  # 按下 Enter 直接查詢現價，不必按按鈕

    def on_calc():
        try:
            buy_price = _to_float(entries["買入價位"].get())
            shares = int(entries["股數"].get())
            current_price = _to_float(entries["現價"].get())
        except ValueError:
            messagebox.showerror("錯誤", "買入價位／股數／現價請輸入數字")
            return
        result_var.set(f"報酬: {profit(buy_price, shares, current_price):.2f}")
    tk.Button(frame, text="計算報酬", command=on_calc).grid(row=len(FIELDS), column=2, padx=8)

    return frame


def build_ui() -> tk.Tk:
    root = tk.Tk()
    root.title("股票損益試算")
    build_stock_frame(root).grid(row=0, column=0)
    return root


if __name__ == "__main__":
    build_ui().mainloop()
