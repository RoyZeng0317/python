"""即時股價抓取與損益計算。

使用證交所公開的即時報價 API（mis.twse.com.tw），不需要申請 API Key。
上市股票代號用 tse_ 前綴查詢，查不到就改用 otc_ 前綴查詢上櫃股票。

抓取失敗（沒有網路、逾時、代號不存在等）時，呼叫端應改用手動輸入現價的
fallback 模式，不能讓程式當掉。
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional, Tuple

QUOTE_API_URL = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"


class StockPriceError(RuntimeError):
    """現價抓取失敗，呼叫端應改走手動輸入現價模式（fallback）。"""


def fetch_price(code: str, timeout: float = 6.0) -> Tuple[float, str]:
    """依股票代號查詢即時成交價，回傳 (現價, 股票名稱)；先查上市（tse_）查不到再查上櫃（otc_）。"""
    code = code.strip()
    if not code:
        raise StockPriceError("股票代號不能為空")

    for market in ("tse", "otc"):
        info = _query(f"{market}_{code}.tw", timeout)
        if info is not None:
            return info
    raise StockPriceError(f"查不到股票代號 {code} 的報價")


def _query(ex_ch: str, timeout: float) -> Optional[Tuple[float, str]]:
    url = QUOTE_API_URL.format(ex_ch=ex_ch)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise StockPriceError(f"現價抓取失敗，請檢查網路連線: {exc}") from exc

    rows = payload.get("msgArray") or []
    if not rows:
        return None

    row = rows[0]
    price_text = row.get("z")
    if price_text in (None, "-", ""):
        price_text = row.get("y")  # 尚未成交時改用昨收價
    if price_text in (None, "-", ""):
        return None

    return float(price_text), row.get("n", "")


def profit(buy_price: float, shares: int, current_price: float) -> float:
    """計算報酬：(現價 - 買入價位) * 股數。"""
    return (current_price - buy_price) * shares
