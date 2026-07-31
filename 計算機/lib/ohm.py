"""完整電學公式：電壓 V、電流 I、電阻 R、功率 P。

輸入任意兩個已知量（其餘留 None），自動推算剩下的量：
V = I * R
P = V * I = I^2 * R = V^2 / R
"""

from __future__ import annotations

from typing import Dict, Optional

VARIABLES = ("V", "I", "R", "P")

UNITS = {"V": "V（伏特）", "I": "A（安培）", "R": "Ω（歐姆）", "P": "W（瓦特）"}


class OhmLawError(ValueError):
    """已知量不足（少於兩個）或已知量彼此矛盾、不合理時拋出。"""


def solve(V: Optional[float] = None, I: Optional[float] = None,
          R: Optional[float] = None, P: Optional[float] = None) -> Dict[str, float]:
    """輸入 V/I/R/P 任兩個已知值，回傳四個變數的完整字典（含原本已知的值）。"""
    values: Dict[str, Optional[float]] = {"V": V, "I": I, "R": R, "P": P}
    known_count = sum(1 for value in values.values() if value is not None)
    if known_count < 2:
        raise OhmLawError("至少需要輸入兩個已知量才能計算")

    if values["V"] is not None and values["I"] is not None:
        if values["R"] is None:
            if values["I"] == 0:
                raise OhmLawError("電流不可為 0")
            values["R"] = values["V"] / values["I"]
        if values["P"] is None:
            values["P"] = values["V"] * values["I"]
    elif values["V"] is not None and values["R"] is not None:
        if values["R"] == 0:
            raise OhmLawError("電阻不可為 0")
        if values["I"] is None:
            values["I"] = values["V"] / values["R"]
        if values["P"] is None:
            values["P"] = values["V"] * values["I"]
    elif values["V"] is not None and values["P"] is not None:
        if values["V"] == 0:
            raise OhmLawError("電壓不可為 0")
        if values["I"] is None:
            values["I"] = values["P"] / values["V"]
        if values["R"] is None:
            if values["I"] == 0:
                raise OhmLawError("電流不可為 0，無法反推電阻")
            values["R"] = values["V"] / values["I"]
    elif values["I"] is not None and values["R"] is not None:
        if values["V"] is None:
            values["V"] = values["I"] * values["R"]
        if values["P"] is None:
            values["P"] = values["I"] * values["V"]
    elif values["I"] is not None and values["P"] is not None:
        if values["I"] == 0:
            raise OhmLawError("電流不可為 0")
        if values["V"] is None:
            values["V"] = values["P"] / values["I"]
        if values["R"] is None:
            values["R"] = values["V"] / values["I"]
    elif values["R"] is not None and values["P"] is not None:
        if values["R"] < 0 or values["P"] < 0:
            raise OhmLawError("電阻與功率需為正值")
        if values["I"] is None:
            values["I"] = (values["P"] / values["R"]) ** 0.5
        if values["V"] is None:
            values["V"] = values["I"] * values["R"]
    else:
        raise OhmLawError("已知量組合無法求解")

    if any(value is None for value in values.values()):
        raise OhmLawError("已知量組合無法求解")
    return values  # type: ignore[return-value]
