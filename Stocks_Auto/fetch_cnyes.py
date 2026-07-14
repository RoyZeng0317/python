"""M2 擷取器：鉅亨網 (cnyes)。
無官方RSS（見 RESEARCH.md Findings #2），改用 HTML 爬蟲：
1. 抓首頁 https://news.cnyes.com/news/cat/headline 的列表頁，正規表示式抽出
   (news_id, title) pair（headline 頁為 React server-render，標題以
   `news/id/<id}"><div title="...">` pattern 直接出現在原始 HTML，已於開發時
   實際 WebFetch 驗證過此 pattern 穩定存在，見 BUILD_LOG.md）。
2. 逐篇 GET 文章頁 https://news.cnyes.com/news/id/<id>，
   - datePublished 從內嵌 JSON `"datePublished":"..."` 正規表示式取得（UTC，轉台北時區）
   - 內文用 fetch_common.extract_body_from_paragraphs 擷取 <p> 文字
"""
import datetime
import re

from bs4 import BeautifulSoup

import config
from fetch_common import fetch_html, extract_body_from_paragraphs

TAIPEI_TZ = datetime.timezone(datetime.timedelta(hours=8))
LISTING_URL = "https://news.cnyes.com/news/cat/headline"
ID_TITLE_RE = re.compile(r'news/id/(\d+)"><div title="([^"]+)"')
DATE_RE = re.compile(r'"datePublished":"([^"]+)"')


def _parse_pubdate(raw):
    try:
        dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.astimezone(TAIPEI_TZ)
    except Exception:
        return None


def fetch(limit=20):
    """回傳鉅亨網最新新聞清單，每筆含 title/link/pubdate/body/description/source。"""
    resp = fetch_html(LISTING_URL)
    if resp is None:
        print("[cnyes] 列表頁擷取失敗，略過此來源")
        return []

    pairs = ID_TITLE_RE.findall(resp.text)
    if not pairs:
        print("[cnyes] 列表頁未解析到任何文章，可能頁面結構已變更，略過此來源")
        return []

    seen = {}
    for news_id, title in pairs:
        seen.setdefault(news_id, title)

    articles = []
    for news_id, title in list(seen.items())[:limit]:
        url = f"https://news.cnyes.com/news/id/{news_id}"
        aresp = fetch_html(url)
        if aresp is None:
            continue
        soup = BeautifulSoup(aresp.text, "html.parser")
        m = DATE_RE.search(aresp.text)
        pubdate = _parse_pubdate(m.group(1)) if m else None
        body = extract_body_from_paragraphs(soup)
        if not body:
            continue
        articles.append(
            {
                "title": title,
                "link": url,
                "pubdate": pubdate,
                "body": body,
                # Revision Round 1（回應 REVIEW.md MAJOR）：不要在擷取端把
                # description 剛好截到等於 summarize.SUMMARY_MAX_LEN(150)，
                # 否則 summarize.py 的 `len(text) > SUMMARY_MAX_LEN` 判斷恆為
                # False，省略號永遠不會被加上。改傳完整 body，交由 summarize.py
                # 統一決定是否截斷、是否加"…"。
                "description": body,
                "source": "cnyes",
            }
        )
    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
