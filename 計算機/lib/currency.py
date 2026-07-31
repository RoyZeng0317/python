"""即時匯率抓取與換算。

使用免金鑰的公開匯率 API（open.er-api.com），不需要申請 API Key。
台灣銀行牌告匯率頁面（rate.bot.com.tw）目前有機器人驗證機制，程式無法直接
抓取，因此改用這個可正常存取的公開來源。

抓取失敗（沒有網路、逾時、API 掛掉等）時，呼叫端應改用 manual_convert()
讓使用者手動輸入匯率計算，不能讓整個程式當掉。
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Dict, Optional

RATE_API_URL = "https://open.er-api.com/v6/latest/{base}"
CACHE_TTL_SECONDS = 300  # 5 分鐘內重複查詢同一個基準幣別直接用快取

CURRENCY_NAMES: Dict[str, str] = {
    "TWD": "新台幣",
    "USD": "美元",
    "JPY": "日圓",
    "EUR": "歐元",
    "CNY": "人民幣",
    "HKD": "港幣",
    "GBP": "英鎊",
    "AUD": "澳幣",
    "KRW": "韓元",
    "SGD": "新加坡幣",
}

_cache: Dict[str, "tuple[float, Dict[str, float]]"] = {}


class ExchangeRateError(RuntimeError):
    """匯率抓取失敗，呼叫端應改走手動輸入模式（fallback）。"""


def fetch_rates(base: str = "USD", timeout: float = 6.0) -> Dict[str, float]:
    """取得以 base 為基準的即時匯率字典；5 分鐘內重複呼叫會使用快取。"""
    base = base.upper()
    cached = _cache.get(base)
    if cached and (time.time() - cached[0]) < CACHE_TTL_SECONDS:
        return cached[1]

    url = RATE_API_URL.format(base=base)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise ExchangeRateError(f"匯率抓取失敗，請檢查網路連線: {exc}") from exc

    if payload.get("result") != "success":
        raise ExchangeRateError("匯率 API 回傳異常")

    rates = payload.get("rates")
    if not rates:
        raise ExchangeRateError("匯率 API 未回傳匯率資料")

    _cache[base] = (time.time(), rates)
    return rates


def convert(amount: float, from_currency: str, to_currency: str) -> float:
    """把 amount 從 from_currency 即時換算成 to_currency（內部會自動抓取/使用快取匯率）。"""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    if from_currency == to_currency:
        return amount

    rates = fetch_rates(base=from_currency)
    if to_currency not in rates:
        raise ExchangeRateError(f"找不到 {to_currency} 的匯率資料")
    return amount * rates[to_currency]


def manual_convert(amount: float, rate: float) -> float:
    """使用者手動輸入匯率時的換算（即時抓取失敗時的 fallback 模式）。"""
    return amount * rate


def last_updated(base: str) -> Optional[float]:
    """回傳指定基準幣別快取的抓取時間（epoch 秒），沒有快取則回傳 None。"""
    cached = _cache.get(base.upper())
    return cached[0] if cached else None
