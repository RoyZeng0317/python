# 連線到 C:\Users\roy\Documents\GitHub\python\basic\advance\library.sql
# 註解下方程式碼不可刪除
import tkinter as tk
import sqlite3

DB = r"C:\Users\roy\Documents\GitHub\python\basic\advance\library.sql"

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
with open(DB, "r", encoding="utf-8") as f:
    cursor.executescript(f.read())
conn.commit()


def search_book():
    keyword = entry.get()
    cursor.execute(
        "SELECT book_type, book_stock FROM library WHERE book_name = ? OR book_id = ?",
        (keyword, keyword),
    )
    row = cursor.fetchone()

    if row:
        book_type, book_stock = row
        result_label.config(text=f"書籍類型:{book_type}, 書籍貨架:{book_stock}")
    else:
        result_label.config(text="查無此書")

# 圖書查詢
search_win = tk.Tk()
search_win.title("圖書查詢")
search_win.geometry("")

search_frame = tk.LabelFrame(search_win, text="查詢")
search_frame.pack(side="top", fill="x", padx=8, pady=8)

tk.Label(search_frame, text="條碼:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
tk.Entry(search_frame).grid(row=0, column=1, sticky="w", padx=4, pady=2)  # book_name 在 SQL 中


win = tk.Tk()
win.title("圖書館書籍查詢")
win.geometry("800x600")

tk.Label(win, text="輸入欲查詢的書名").pack(pady=10)

entry = tk.Entry(win, width=40)
entry.pack(pady=5)

tk.Button(win, text="查詢", command=search_book).pack(pady=5)

result_label = tk.Label(win, text="", font=("Arial", 14))
result_label.pack(pady=20)

win.mainloop()
