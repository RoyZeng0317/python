"""基本四則運算核心邏輯（不依賴 tkinter，純運算狀態機）。"""

from __future__ import annotations

from typing import Optional

OPERATORS = ("+", "-", "*", "/")


def apply_operator(left: float, operator: str, right: float) -> float:
    """對兩個數字套用四則運算子，回傳結果。"""
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("除數不可為 0")
        return left / right
    raise ValueError(f"不支援的運算子: {operator}")


def format_number(value: float) -> str:
    """把浮點數格式化成計算機顯示用字串（整數不顯示小數點）。"""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.10f}".rstrip("0").rstrip(".")
    return text or "0"


class CalculatorEngine:
    """單一運算子的計算機狀態機：數字 -> 運算子 -> 數字 -> 等於。"""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.display = "0"
        self._pending_value: Optional[float] = None
        self._pending_operator: Optional[str] = None
        self._just_evaluated = False

    def input_digit(self, digit: str) -> str:
        if self._just_evaluated:
            self.display = "0"
            self._just_evaluated = False
        self.display = digit if self.display == "0" else self.display + digit
        return self.display

    def input_decimal_point(self) -> str:
        if self._just_evaluated:
            self.display = "0"
            self._just_evaluated = False
        if "." not in self.display:
            self.display += "."
        return self.display

    def toggle_sign(self) -> str:
        if self.display.startswith("-"):
            self.display = self.display[1:]
        elif self.display != "0":
            self.display = "-" + self.display
        return self.display

    def backspace(self) -> str:
        if self._just_evaluated:
            self.reset()
            return self.display
        self.display = self.display[:-1] or "0"
        return self.display

    def input_operator(self, operator: str) -> str:
        if operator not in OPERATORS:
            raise ValueError(f"不支援的運算子: {operator}")
        if self._pending_operator is not None and not self._just_evaluated:
            # 連續按運算子時先計算前一步，才能連鎖運算（如 2 + 3 + 4）
            self._evaluate_pending()
        else:
            self._pending_value = float(self.display)
        self._pending_operator = operator
        self._just_evaluated = False
        self.display = "0"
        return self.display

    def _evaluate_pending(self) -> None:
        if self._pending_operator is None or self._pending_value is None:
            return
        current = float(self.display)
        result = apply_operator(self._pending_value, self._pending_operator, current)
        self._pending_value = result
        self.display = format_number(result)

    def equals(self) -> str:
        if self._pending_operator is None:
            return self.display
        self._evaluate_pending()
        self._pending_operator = None
        self._just_evaluated = True
        return self.display
