"""電阻 / 電容數值換算：數字碼與色環雙向換算。

換算邏輯放在 lib/resistor_capacitor.py（不依賴 tkinter），這支檔案只負責畫面
與事件處理，可被 計算機.py 當分頁掛載，也能單獨執行。
"""

import tkinter as tk
from tkinter import messagebox, ttk

from lib import resistor_capacitor as rc


def format_ohms(ohms: float) -> str:
    """把歐姆數值格式化成 Ω / kΩ / MΩ，方便閱讀。"""
    if ohms >= 1_000_000:
        return f"{ohms / 1_000_000:.4g} MΩ"
    if ohms >= 1_000:
        return f"{ohms / 1_000:.4g} kΩ"
    return f"{ohms:.4g} Ω"


class ResistorCapacitorTab(ttk.Frame):
    """電阻 / 電容數值換算分頁：數字碼與色環雙向換算。"""

    MODES = ("電阻數字碼", "電阻色環", "電容數字碼", "電容色環")

    def __init__(self, parent: tk.Misc) -> None:
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


if __name__ == "__main__":
    root = tk.Tk()
    root.title("電阻/電容換算")
    ResistorCapacitorTab(root).pack(fill="both", expand=True)
    root.mainloop()
