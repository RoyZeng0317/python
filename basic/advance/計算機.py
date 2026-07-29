import tkinter as tk

BG_COLOR = "#1e1e1e"
KEY_BG = "#2d2d2d"
KEY_FG = "#ffffff"
KEY_ACTIVE_BG = "#3d3d3d"
KEY_FONT = ("Segoe UI", 20, "bold")
DISPLAY_FONT = ("Segoe UI", 28, "bold")


def make_key(parent, text, command=None):
    return tk.Button(
        parent,
        text=text,
        width=4,
        height=2,
        font=KEY_FONT,
        bg=KEY_BG,
        fg=KEY_FG,
        activebackground=KEY_ACTIVE_BG,
        activeforeground=KEY_FG,
        relief="flat",
        bd=0,
        command=command or "",
    )

def 匯率():
    # 從台灣銀行取得即時匯率
    URL = "https://rate.bot.com.tw/xrt?Lang=zh-TW"

def claculate():
    match claculate:
        case "+":
            ...
        case "-":
            ...
        case "/":
            ...
        case "*":
            ...
        
def main():
    root = tk.Tk()
    root.title("計算機")
    root.configure(bg=BG_COLOR)

    keypad = [
        [7, 8, 9],
        [4, 5, 6],
        [1, 2, 3],
    ]

    frame = tk.Frame(root, bg=BG_COLOR, padx=10, pady=10)
    frame.grid()

    result_var = tk.StringVar(value="0")

    def press_digit(digit):
        current = result_var.get()
        result_var.set(digit if current == "0" else current + digit)

    result_label = tk.Label(
        frame,
        textvariable=result_var,
        font=DISPLAY_FONT,
        bg=BG_COLOR,
        fg=KEY_FG,
        anchor="e",
        padx=10,
    )
    result_label.grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="ew")

    for row_index, row in enumerate(keypad):
        for col_index, number in enumerate(row):
            make_key(
                frame, str(number), command=lambda n=number: press_digit(str(n))
            ).grid(row=row_index + 1, column=col_index, padx=6, pady=6)

    make_key(frame, "0", command=lambda: press_digit("0")).grid(
        row=4, column=0, columnspan=3, padx=6, pady=6, sticky="ew"
    )

    root.mainloop()


if __name__ == "__main__":
    main()
