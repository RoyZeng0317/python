"""M2 擷取器：經濟日報 (money.udn.com)。
無官方RSS（見 RESEARCH.md Findings #2），改用 HTML 爬蟲：
首頁 https://money.udn.com/money/index 內嵌一段 JSON-LD
(`<script type="application/ld+json">`)，其中 `mainEntity.itemListElement`
即為首頁精選新聞列表，含 headline/url/datePublished/description，
已於開發時實際 WebFetch 驗證存在（見 BUILD_LOG.md）。
description 欄位僅約100字且常被截斷，故仍逐篇擷取文章頁全文供600字規則判斷。
"""
import datetime
import json
import re

from bs4 import BeautifulSoup

import config
from fetch_common import fetch_html, extract_body_from_paragraphs

LISTING_URL = "https://money.udn.com/money/index"
LD_JSON_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL
)


def _parse_pubdate(raw):
    try:
        return datetime.datetime.fromisoformat(raw)
    except Exception:
        return None


def fetch(limit=20):
    """回傳經濟日報首頁精選新聞清單，每筆含 title/link/pubdate/body/description/source。"""
    resp = fetch_html(LISTING_URL)
    if resp is None:
        print("[udn] 列表頁擷取失敗，略過此來源")
        return []

    blocks = LD_JSON_RE.findall(resp.text)
    items = []
    for block in blocks:
        try:
            data = json.loads(block, strict=False)
        except Exception:
            continue
        main_entity = data.get("mainEntity") if isinstance(data, dict) else None
        if isinstance(main_entity, dict) and main_entity.get("@type") == "ItemList":
            items = main_entity.get("itemListElement", [])
            break

    if not items:
        print("[udn] 首頁 JSON-LD 未解析到新聞列表，可能頁面結構已變更，略過此來源")
        return []

    articles = []
    for it in items[:limit]:
        item = it.get("item", it)
        title = item.get("headline") or item.get("name")
        url = item.get("url")
        pubdate = _parse_pubdate(item.get("datePublished") or "")
        description = (item.get("description") or "").strip()
        if not title or not url:
            continue

        aresp = fetch_html(url)
        body = ""
        if aresp is not None:
            soup = BeautifulSoup(aresp.text, "html.parser")
            body = extract_body_from_paragraphs(soup)
        if not body:
            body = description

        articles.append(
            {
                "title": title,
                "link": url,
                "pubdate": pubdate,
                "body": body,
                # Revision Round 1（回應 REVIEW.md MAJOR）：description 若為原生
                # 提供則直接使用（通常本來就不到150字，不受此bug影響）；若為空才
                # fallback 到 body，但 fallback 也不能剛好截到150字，否則
                # summarize.py 的截斷判斷會恆為 False、永遠不加"…"。改傳完整
                # body，由 summarize.py 統一決定截斷與省略號。
                "description": description or body,
                "source": "udn",
            }
        )
    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
