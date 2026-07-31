"""電阻與電容數值換算：數字碼（如貼片電阻 103、陶瓷電容 104）與色環對照，雙向換算。"""

from __future__ import annotations

from typing import List, Optional, Tuple

# EIA 標準色碼表：數值色環顏色 -> 數字
DIGIT_COLORS = ["黑", "棕", "紅", "橙", "黃", "綠", "藍", "紫", "灰", "白"]
DIGIT_VALUES = {color: index for index, color in enumerate(DIGIT_COLORS)}

# 乘數色環顏色 -> 乘數倍率
MULTIPLIER_COLORS = {
    "黑": 1,
    "棕": 10,
    "紅": 100,
    "橙": 1_000,
    "黃": 10_000,
    "綠": 100_000,
    "藍": 1_000_000,
    "紫": 10_000_000,
    "灰": 100_000_000,
    "白": 1_000_000_000,
    "金": 0.1,
    "銀": 0.01,
}

# 誤差（容差）色環顏色 -> 標示文字
TOLERANCE_COLORS = {
    "棕": "±1%",
    "紅": "±2%",
    "綠": "±0.5%",
    "藍": "±0.25%",
    "紫": "±0.1%",
    "灰": "±0.05%",
    "金": "±5%",
    "銀": "±10%",
    "無": "±20%",
}


# ---------------------------------------------------------------------------
# 電阻：數字碼（貼片電阻 SMD code）
# ---------------------------------------------------------------------------

def resistor_code_to_ohms(code: str) -> float:
    """貼片電阻數字碼 -> 電阻值（歐姆）。例："103" -> 10000、"4R7" -> 4.7。"""
    code = code.strip().upper()
    if not code:
        raise ValueError("請輸入電阻數字碼")
    if "R" in code:
        whole, _, frac = code.partition("R")
        return float(f"{whole or '0'}.{frac or '0'}")
    if not code.isdigit() or len(code) not in (3, 4):
        raise ValueError("電阻數字碼需為 3 或 4 位數字，或使用 R 表示小數點（如 4R7）")
    significant = int(code[:-1])
    multiplier = int(code[-1])
    return significant * (10 ** multiplier)


def ohms_to_resistor_code(ohms: float, significant_digits: int = 3) -> str:
    """電阻值（歐姆）-> 貼片電阻數字碼（最佳近似值）。"""
    if ohms <= 0:
        raise ValueError("電阻值必須大於 0")
    if ohms < 10:
        whole = int(ohms)
        frac = round((ohms - whole) * 10)
        return f"{whole}R{frac}"
    value = ohms
    exponent = 0
    upper_bound = 10 ** significant_digits
    while value >= upper_bound:
        value /= 10
        exponent += 1
    return f"{round(value):0{significant_digits}d}{exponent}"


# ---------------------------------------------------------------------------
# 電阻：色環
# ---------------------------------------------------------------------------

def resistor_bands_to_ohms(colors: List[str], band_count: int = 4) -> Tuple[float, str]:
    """色環電阻（4 環或 5 環）顏色列表 -> (電阻值歐姆, 誤差標示)。"""
    if band_count not in (4, 5):
        raise ValueError("色環電阻僅支援 4 環或 5 環")
    colors = [c.strip() for c in colors]
    if len(colors) != band_count:
        raise ValueError(f"請輸入 {band_count} 個顏色")

    digit_count = 2 if band_count == 4 else 3
    digit_bands = colors[:digit_count]
    multiplier_band = colors[digit_count]
    tolerance_band = colors[-1]

    try:
        digits = [DIGIT_VALUES[c] for c in digit_bands]
    except KeyError as exc:
        raise ValueError(f"無效的數值色環顏色: {exc.args[0]}") from exc
    if multiplier_band not in MULTIPLIER_COLORS:
        raise ValueError(f"無效的乘數色環顏色: {multiplier_band}")

    significant = int("".join(str(d) for d in digits))
    ohms = significant * MULTIPLIER_COLORS[multiplier_band]
    tolerance = TOLERANCE_COLORS.get(tolerance_band, "±20%")
    return ohms, tolerance


def ohms_to_resistor_bands(ohms: float, band_count: int = 4) -> List[str]:
    """電阻值（歐姆）-> 色環顏色列表（最佳近似值，誤差環固定給金 ±5%）。"""
    if ohms <= 0:
        raise ValueError("電阻值必須大於 0")
    digit_count = 2 if band_count == 4 else 3
    upper_bound = 10 ** digit_count
    value = ohms
    exponent = 0
    while value >= upper_bound:
        value /= 10
        exponent += 1
    while value < upper_bound / 10 and exponent > -2:
        value *= 10
        exponent -= 1

    multiplier_color = next((c for c, m in MULTIPLIER_COLORS.items() if m == 10 ** exponent), None)
    if multiplier_color is None:
        raise ValueError("此電阻值無法用標準色環乘數表示")

    significant = str(round(value)).zfill(digit_count)[:digit_count]
    digit_colors = [DIGIT_COLORS[int(d)] for d in significant]
    return digit_colors + [multiplier_color, "金"]


# ---------------------------------------------------------------------------
# 電容：數字碼（如陶瓷電容 104）
# ---------------------------------------------------------------------------

def capacitor_code_to_farads(code: str) -> float:
    """電容數字碼 -> 電容值（法拉 F）。例："104" -> 10*10^4 pF = 0.1µF。"""
    code = code.strip().upper()
    if not code:
        raise ValueError("請輸入電容數字碼")

    if "R" in code:
        # 例如 4R7 代表 4.7pF，用於標示小容值
        whole, _, frac = code.partition("R")
        pico_farads = float(f"{whole or '0'}.{frac or '0'}")
    elif code.isdigit() and len(code) == 3:
        significant = int(code[:2])
        multiplier = int(code[2])
        pico_farads = significant * (10 ** multiplier)
    elif code.replace(".", "", 1).isdigit():
        # 部分小電容直接標示 pF 數值，如 "47" 代表 47pF
        pico_farads = float(code)
    else:
        raise ValueError("無法辨識的電容數字碼格式")

    return pico_farads * 1e-12


def farads_to_capacitor_code(farads: float) -> str:
    """電容值（法拉 F）-> 電容數字碼（最佳近似值）。"""
    if farads <= 0:
        raise ValueError("電容值必須大於 0")
    pico_farads = farads * 1e12
    if pico_farads < 10:
        whole = int(pico_farads)
        frac = round((pico_farads - whole) * 10)
        return f"{whole}R{frac}"
    value = pico_farads
    exponent = 0
    while value >= 100:
        value /= 10
        exponent += 1
    return f"{round(value):02d}{exponent}"


def format_capacitance(farads: float) -> str:
    """把法拉數值格式化成人類慣用單位（pF / nF / µF）字串。"""
    if farads >= 1e-6:
        return f"{farads * 1e6:.4g} µF"
    if farads >= 1e-9:
        return f"{farads * 1e9:.4g} nF"
    return f"{farads * 1e12:.4g} pF"


# ---------------------------------------------------------------------------
# 電容：色環（早期陶瓷/薄膜電容，沿用與電阻相同的 EIA 色碼表，單位為 pF）
# ---------------------------------------------------------------------------

def capacitor_bands_to_farads(colors: List[str]) -> Tuple[float, Optional[str]]:
    """色環電容（3 或 4 環）顏色列表 -> (電容值法拉, 誤差標示或 None)。"""
    if len(colors) not in (3, 4):
        raise ValueError("色環電容請輸入 3 個顏色（不含誤差環）或 4 個顏色（含誤差環）")
    colors = [c.strip() for c in colors]

    digit_bands = colors[:2]
    multiplier_band = colors[2]
    tolerance_band = colors[3] if len(colors) == 4 else None

    try:
        digits = [DIGIT_VALUES[c] for c in digit_bands]
    except KeyError as exc:
        raise ValueError(f"無效的數值色環顏色: {exc.args[0]}") from exc
    if multiplier_band not in MULTIPLIER_COLORS:
        raise ValueError(f"無效的乘數色環顏色: {multiplier_band}")

    significant = int("".join(str(d) for d in digits))
    pico_farads = significant * MULTIPLIER_COLORS[multiplier_band]
    tolerance = TOLERANCE_COLORS.get(tolerance_band) if tolerance_band else None
    return pico_farads * 1e-12, tolerance
