"""計算機：基本四則運算 + 匯率換算 + 電阻/電容數值換算 + 電學公式（歐姆定律）。

所有核心運算邏輯都放在 lib/ 資料夾（不依賴 tkinter），這支檔案只負責畫面
與事件處理，方便日後 Flutter/Dart 版本沿用同一套 lib 運算規格。
"""
# 不要更換簡易 library(下方不可改回原本-> import time)
import threading, time
import tkinter as tk
import 電阻值計算, Ohm_Law
from tkinter import messagebox, ttk

from lib import basic_calc, currency, ohm
from lib import resistor_capacitor as rc

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


class CurrencyTab(ttk.Frame):
    """匯率換算分頁：即時連網抓取，抓取失敗時可改用手動輸入匯率。"""

    def __init__(self, parent: tk.Widget) -> None:
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

    def on_failure(self, _message: str) -> None:
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


class ResistorCapacitorTab(ttk.Frame):
    """電阻 / 電容數值換算分頁：數字碼與色環雙向換算。"""

    MODES = ("電阻數字碼", "電阻色環", "電容數字碼", "電容色環")

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, padding=16)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        top = ttk.Frame(self)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(top, text="換算模式").pack(side="left")
        self.mode_var = tk.StringVar(value=self.MODES[0])
        mode_box = ttk.Combobox(
            top, textvariable=self.mode_var, values=self.MODES, state="readonly", width=16
        )
        mode_box.pack(side="left", padx=8)
        mode_box.bind("<<ComboboxSelected>>", lambda e: self.show_mode())

        self.content = ttk.Frame(self)
        self.content.grid(row=1, column=0, sticky="nsew")
        self.content.columnconfigure(0, weight=1)

        self.frames = {
            "電阻數字碼": self._build_resistor_code_frame(self.content),
            "電阻色環": self._build_resistor_band_frame(self.content),
            "電容數字碼": self._build_capacitor_code_frame(self.content),
            "電容色環": self._build_capacitor_band_frame(self.content),
        }
        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_mode()

    def show_mode(self) -> None:
        self.frames[self.mode_var.get()].tkraise()

    # ---- 電阻數字碼 -----------------------------------------------------
    def _build_resistor_code_frame(self, parent: tk.Widget) -> ttk.Frame:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="數字碼 -> 電阻值（如貼片電阻 103、4R7）", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        self.res_code_var = tk.StringVar(value="104")
        ttk.Entry(frame, textvariable=self.res_code_var, width=12).grid(row=1, column=0, sticky="w")
        ttk.Button(frame, text="轉換", command=self.on_resistor_code_to_ohms).grid(row=1, column=1, padx=6)
        self.res_code_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.res_code_result, font=("Segoe UI", 13, "bold")).grid(
            row=1, column=2, sticky="w"
        )

        ttk.Separator(frame).grid(row=2, column=0, columnspan=3, sticky="ew", pady=12)

        ttk.Label(frame, text="電阻值(Ω) -> 數字碼", font=("Segoe UI", 12, "bold")).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        self.res_ohms_var = tk.StringVar(value="10000")
        ttk.Entry(frame, textvariable=self.res_ohms_var, width=12).grid(row=4, column=0, sticky="w")
        ttk.Button(frame, text="轉換", command=self.on_ohms_to_resistor_code).grid(row=4, column=1, padx=6)
        self.res_ohms_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.res_ohms_result, font=("Segoe UI", 13, "bold")).grid(
            row=4, column=2, sticky="w"
        )
        return frame

    def on_resistor_code_to_ohms(self) -> None:
        try:
            ohms = rc.resistor_code_to_ohms(self.res_code_var.get())
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.res_code_result.set(format_ohms(ohms))

    def on_ohms_to_resistor_code(self) -> None:
        try:
            ohms = float(self.res_ohms_var.get())
            code = rc.ohms_to_resistor_code(ohms)
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.res_ohms_result.set(code)

    # ---- 電阻色環 --------------------------------------------------------
    def _build_resistor_band_frame(self, parent: tk.Widget) -> ttk.Frame:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="色環 -> 電阻值", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=6, sticky="w", pady=(0, 6)
        )

        ttk.Label(frame, text="環數").grid(row=1, column=0, sticky="w")
        self.res_band_count_var = tk.StringVar(value="4")
        band_count_box = ttk.Combobox(
            frame, textvariable=self.res_band_count_var, values=("4", "5"), state="readonly", width=4
        )
        band_count_box.grid(row=1, column=1, sticky="w")
        band_count_box.bind("<<ComboboxSelected>>", lambda e: self._update_resistor_band_visibility())

        digit_colors = rc.DIGIT_COLORS
        multiplier_colors = list(rc.MULTIPLIER_COLORS.keys())
        tolerance_colors = list(rc.TOLERANCE_COLORS.keys())

        self.res_band_vars = [tk.StringVar(value=digit_colors[0]) for _ in range(3)]
        self.res_band_boxes = []
        labels = ("第1環", "第2環", "第3環(5環才有)")
        for i in range(3):
            ttk.Label(frame, text=labels[i]).grid(row=2, column=i, sticky="w", padx=4)
            box = ttk.Combobox(
                frame, textvariable=self.res_band_vars[i], values=digit_colors, state="readonly", width=6
            )
            box.grid(row=3, column=i, padx=4)
            self.res_band_boxes.append(box)

        self.res_mult_var = tk.StringVar(value="紅")
        ttk.Label(frame, text="乘數環").grid(row=2, column=3, sticky="w", padx=4)
        ttk.Combobox(
            frame, textvariable=self.res_mult_var, values=multiplier_colors, state="readonly", width=6
        ).grid(row=3, column=3, padx=4)

        self.res_tol_var = tk.StringVar(value="金")
        ttk.Label(frame, text="誤差環").grid(row=2, column=4, sticky="w", padx=4)
        ttk.Combobox(
            frame, textvariable=self.res_tol_var, values=tolerance_colors, state="readonly", width=6
        ).grid(row=3, column=4, padx=4)

        ttk.Button(frame, text="轉換為電阻值", command=self.on_resistor_bands_to_ohms).grid(
            row=4, column=0, columnspan=5, sticky="w", pady=10
        )
        self.res_band_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.res_band_result, font=("Segoe UI", 13, "bold")).grid(
            row=5, column=0, columnspan=5, sticky="w"
        )

        ttk.Separator(frame).grid(row=6, column=0, columnspan=6, sticky="ew", pady=12)

        ttk.Label(frame, text="電阻值(Ω) -> 色環", font=("Segoe UI", 12, "bold")).grid(
            row=7, column=0, columnspan=6, sticky="w", pady=(0, 6)
        )
        self.res_band_reverse_ohms_var = tk.StringVar(value="1000")
        ttk.Entry(frame, textvariable=self.res_band_reverse_ohms_var, width=12).grid(row=8, column=0, sticky="w")
        ttk.Button(frame, text="轉換", command=self.on_ohms_to_resistor_bands).grid(row=8, column=1, padx=6)
        self.res_band_reverse_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.res_band_reverse_result, font=("Segoe UI", 13, "bold")).grid(
            row=9, column=0, columnspan=5, sticky="w"
        )

        self._update_resistor_band_visibility()
        return frame

    def _update_resistor_band_visibility(self) -> None:
        if self.res_band_count_var.get() == "5":
            self.res_band_boxes[2].grid()
        else:
            self.res_band_boxes[2].grid_remove()

    def on_resistor_bands_to_ohms(self) -> None:
        band_count = int(self.res_band_count_var.get())
        digit_count = 2 if band_count == 4 else 3
        colors = [var.get() for var in self.res_band_vars[:digit_count]]
        colors += [self.res_mult_var.get(), self.res_tol_var.get()]
        try:
            ohms, tolerance = rc.resistor_bands_to_ohms(colors, band_count)
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.res_band_result.set(f"{format_ohms(ohms)}（誤差 {tolerance}）")

    def on_ohms_to_resistor_bands(self) -> None:
        try:
            ohms = float(self.res_band_reverse_ohms_var.get())
            band_count = int(self.res_band_count_var.get())
            colors = rc.ohms_to_resistor_bands(ohms, band_count)
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.res_band_reverse_result.set(" - ".join(colors))

    # ---- 電容數字碼 ------------------------------------------------------
    def _build_capacitor_code_frame(self, parent: tk.Widget) -> ttk.Frame:
        frame = ttk.Frame(parent)
        ttk.Label(
            frame, text="數字碼 -> 電容值（如陶瓷電容 104）", font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
        self.cap_code_var = tk.StringVar(value="104")
        ttk.Entry(frame, textvariable=self.cap_code_var, width=12).grid(row=1, column=0, sticky="w")
        ttk.Button(frame, text="轉換", command=self.on_capacitor_code_to_farads).grid(row=1, column=1, padx=6)
        self.cap_code_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.cap_code_result, font=("Segoe UI", 13, "bold")).grid(
            row=1, column=2, sticky="w"
        )

        ttk.Separator(frame).grid(row=2, column=0, columnspan=3, sticky="ew", pady=12)

        ttk.Label(frame, text="電容值 -> 數字碼", font=("Segoe UI", 12, "bold")).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 6)
        )
        self.cap_value_var = tk.StringVar(value="100")
        ttk.Entry(frame, textvariable=self.cap_value_var, width=12).grid(row=4, column=0, sticky="w")
        self.cap_unit_var = tk.StringVar(value="nF")
        ttk.Combobox(
            frame, textvariable=self.cap_unit_var, values=("pF", "nF", "µF"), state="readonly", width=6
        ).grid(row=4, column=1, sticky="w", padx=4)
        ttk.Button(frame, text="轉換", command=self.on_farads_to_capacitor_code).grid(row=4, column=2, padx=6)
        self.cap_value_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.cap_value_result, font=("Segoe UI", 13, "bold")).grid(
            row=5, column=0, columnspan=3, sticky="w"
        )
        return frame

    def on_capacitor_code_to_farads(self) -> None:
        try:
            farads = rc.capacitor_code_to_farads(self.cap_code_var.get())
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.cap_code_result.set(rc.format_capacitance(farads))

    def on_farads_to_capacitor_code(self) -> None:
        unit_factor = {"pF": 1e-12, "nF": 1e-9, "µF": 1e-6}
        try:
            value = float(self.cap_value_var.get())
            farads = value * unit_factor[self.cap_unit_var.get()]
            code = rc.farads_to_capacitor_code(farads)
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        self.cap_value_result.set(code)

    # ---- 電容色環 --------------------------------------------------------
    def _build_capacitor_band_frame(self, parent: tk.Widget) -> ttk.Frame:
        frame = ttk.Frame(parent)
        ttk.Label(frame, text="色環電容 -> 電容值", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6)
        )

        digit_colors = rc.DIGIT_COLORS
        multiplier_colors = list(rc.MULTIPLIER_COLORS.keys())
        tolerance_colors = ["(未標示)"] + list(rc.TOLERANCE_COLORS.keys())

        self.cap_band_vars = [tk.StringVar(value=digit_colors[0]) for _ in range(2)]
        labels = ("第1環", "第2環")
        for i in range(2):
            ttk.Label(frame, text=labels[i]).grid(row=1, column=i, sticky="w", padx=4)
            ttk.Combobox(
                frame, textvariable=self.cap_band_vars[i], values=digit_colors, state="readonly", width=6
            ).grid(row=2, column=i, padx=4)

        self.cap_mult_var = tk.StringVar(value="紅")
        ttk.Label(frame, text="乘數環").grid(row=1, column=2, sticky="w", padx=4)
        ttk.Combobox(
            frame, textvariable=self.cap_mult_var, values=multiplier_colors, state="readonly", width=6
        ).grid(row=2, column=2, padx=4)

        self.cap_tol_var = tk.StringVar(value="(未標示)")
        ttk.Label(frame, text="誤差環(可不選)").grid(row=1, column=3, sticky="w", padx=4)
        ttk.Combobox(
            frame, textvariable=self.cap_tol_var, values=tolerance_colors, state="readonly", width=8
        ).grid(row=2, column=3, padx=4)

        ttk.Button(frame, text="轉換為電容值", command=self.on_capacitor_bands_to_farads).grid(
            row=3, column=0, columnspan=4, sticky="w", pady=10
        )
        self.cap_band_result = tk.StringVar(value="—")
        ttk.Label(frame, textvariable=self.cap_band_result, font=("Segoe UI", 13, "bold")).grid(
            row=4, column=0, columnspan=4, sticky="w"
        )
        return frame

    def on_capacitor_bands_to_farads(self) -> None:
        colors = [var.get() for var in self.cap_band_vars] + [self.cap_mult_var.get()]
        if self.cap_tol_var.get() != "(未標示)":
            colors.append(self.cap_tol_var.get())
        try:
            farads, tolerance = rc.capacitor_bands_to_farads(colors)
        except ValueError as exc:
            messagebox.showerror("輸入錯誤", str(exc))
            return
        text = rc.format_capacitance(farads)
        if tolerance:
            text += f"（誤差 {tolerance}）"
        self.cap_band_result.set(text)


class OhmLawTab(ttk.Frame):
    """電學公式分頁：V、I、R、P 任意輸入兩個已知量，自動算出其餘。"""

    def __init__(self, parent: tk.Widget) -> None:
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
        notebook.add(CurrencyTab(notebook), text="匯率換算")
        notebook.add(ResistorCapacitorTab(notebook), text="電阻/電容")
        notebook.add(OhmLawTab(notebook), text="電學公式")


def main() -> None:
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
