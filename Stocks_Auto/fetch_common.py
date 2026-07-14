"""M2 擷取器共用工具函式：HTML 請求、內文段落擷取。
供 fetch_cnyes.py / fetch_udn.py / fetch_ctee.py / fetch_ptt.py 共用。
"""
import requests

import config

# 各來源文章頁常見的樣板/廣告文字，擷取內文時濾除
BOILERPLATE_MARKERS = [
    "著作權所有", "All Rights Reserved", "剪貼簿", "訂閱方案", "點我下載",
    "加入為", "熱門來源", "延伸閱讀", "更多內容", "信任第一", "景觀 Buffet",
    "APP下載", "下載APP", "立即下載", "掃描QR",
]

# Revision Round 1（回應 REVIEW.md BLOCKER 建議 #3）：
# 「收集所有 <p> 標籤」的通用擷取法，會把「延伸閱讀/相關新聞」側欄或推薦區塊的
# <p> 文字一併併入 body（REVIEW.md 實際案例：「1314 中石化」誤判組，命中字串
# 就是來自側欄推薦文章連結文字，而非本文）。純關鍵字黑名單（BOILERPLATE_MARKERS）
# 只能濾掉「行文字剛好含有這些詞」的段落，濾不掉「這一整個容器就是側欄」的情況。
# 改用 DOM 結構訊號：往上找父層元素的 class/id，若含有下列關鍵字之一，視為
# 側欄/相關文章/廣告容器，整段 <p> 直接排除，不論文字內容為何。
SIDEBAR_CONTAINER_MARKERS = [
    "related", "recommend", "sidebar", "aside", "extend", "read-more",
    "readmore", "promo", "ad-", "advertisement", "widget", "popular",
    "hot-news", "hotnews", "share", "social",
]


def _is_in_sidebar_container(tag):
    """往上檢查祖先元素的 tag 名稱/class/id，判斷這個 <p> 是否位於側欄/相關
    文章/推薦區塊容器內。找不到明確訊號則視為本文（保守，避免誤刪正文）。"""
    for ancestor in tag.parents:
        name = getattr(ancestor, "name", None)
        if name in ("aside",):
            return True
        if name in (None, "[document]", "html", "body"):
            break
        attr_text = " ".join(ancestor.get("class") or []) + " " + (ancestor.get("id") or "")
        attr_text = attr_text.lower()
        if any(marker in attr_text for marker in SIDEBAR_CONTAINER_MARKERS):
            return True
    return False


def fetch_html(url, session=None):
    """GET 一個 URL，回傳 requests.Response；失敗回傳 None（不拋例外，讓呼叫端優雅略過）。"""
    getter = session.get if session is not None else requests.get
    try:
        resp = getter(url, headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as exc:
        print(f"[fetch_common] GET 失敗 {url}: {exc}")
        return None


def extract_body_from_paragraphs(soup, min_len=15, extra_markers=None):
    """規則式內文擷取：collect所有 <p> 文字，濾除過短/樣板行/側欄容器內的段落，
    其餘依原順序合併。"""
    markers = BOILERPLATE_MARKERS + (extra_markers or [])
    paragraphs = []
    for p in soup.find_all("p"):
        text = p.get_text(strip=True)
        if len(text) < min_len:
            continue
        if any(marker in text for marker in markers):
            continue
        if _is_in_sidebar_container(p):
            continue
        paragraphs.append(text)
    return "\n".join(paragraphs)
