"""M2 擷取器：工商時報 (ctee.com.tw)。
無官方RSS（見 RESEARCH.md Findings #2），改用 HTML 爬蟲：
即時新聞頁 https://www.ctee.com.tw/livenews/tw 內嵌一段 JSON-LD `@graph`，
其中一個節點含 `mainEntity.itemListElement`（headline/url/datePublished），
已於開發時實際 WebFetch 驗證存在（見 BUILD_LOG.md）。逐篇擷取文章頁全文
供600字規則判斷。
"""
import datetime
import json
import re

from bs4 import BeautifulSoup

import config
from fetch_common import fetch_html, extract_body_from_paragraphs

LISTING_URL = "https://www.ctee.com.tw/livenews/tw"
LD_JSON_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL
)


def _parse_pubdate(raw):
    try:
        return datetime.datetime.fromisoformat(raw)
    except Exception:
        return None


def _find_item_list(html):
    for block in LD_JSON_RE.findall(html):
        try:
            data = json.loads(block, strict=False)
        except Exception:
            continue
        # 該 script 內容可能是單一 JSON-LD 物件，也可能是一個物件陣列（每個元素各自帶 @graph）
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            graph = candidate.get("@graph") if isinstance(candidate, dict) else None
            if not graph:
                continue
            for node in graph:
                main_entity = node.get("mainEntity") if isinstance(node, dict) else None
                if isinstance(main_entity, dict) and main_entity.get("@type") == "ItemList":
                    return main_entity.get("itemListElement", [])
    return []


def fetch(limit=20):
    """回傳工商時報即時新聞清單，每筆含 title/link/pubdate/body/description/source。"""
    resp = fetch_html(LISTING_URL)
    if resp is None:
        print("[ctee] 列表頁擷取失敗，略過此來源")
        return []

    items = _find_item_list(resp.text)
    if not items:
        print("[ctee] 列表頁 JSON-LD 未解析到新聞列表，可能頁面結構已變更，略過此來源")
        return []

    articles = []
    for it in items[:limit]:
        item = it.get("item", it)
        title = item.get("headline") or item.get("name")
        url = item.get("url")
        pubdate = _parse_pubdate(item.get("datePublished") or "")
        if not title or not url:
            continue

        aresp = fetch_html(url)
        body = ""
        if aresp is not None:
            soup = BeautifulSoup(aresp.text, "html.parser")
            body = extract_body_from_paragraphs(soup)

        articles.append(
            {
                "title": title,
                "link": url,
                "pubdate": pubdate,
                "body": body,
                # Revision Round 1（回應 REVIEW.md MAJOR）：見 fetch_cnyes.py
                # 同樣的說明，改傳完整 body，由 summarize.py 統一截斷+加"…"。
                "description": body,
                "source": "ctee",
            }
        )
    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
