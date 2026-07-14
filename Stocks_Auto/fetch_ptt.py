"""M2 擷取器：PTT Stock 板。
無官方RSS（見 RESEARCH.md Findings #4）。robots.txt 回傳404（無機器可讀規則，
非明文歡迎爬蟲），採業界慣用 over18 cookie 繞過18禁確認頁（技術上成熟、廣泛驗證
的做法，見 RESEARCH.md），PTT無官方ToS明文允許自動化長期抓取，屬灰色地帶，
使用者已於 PLAN.md 知悉此風險（Q2核准PTT並要求Researcher確認可行性，
Researcher結論：技術可行，是否要做是風險承受度問題非純技術問題）。
"""
import datetime
import re

import requests
from bs4 import BeautifulSoup

import config
from fetch_common import fetch_html, extract_body_from_paragraphs

TAIPEI_TZ = datetime.timezone(datetime.timedelta(hours=8))
LISTING_URL = "https://www.ptt.cc/bbs/Stock/index.html"
DATE_FORMAT = "%a %b %d %H:%M:%S %Y"


def _make_session():
    session = requests.Session()
    session.cookies.set("over18", "1")
    return session


def _parse_pubdate(raw):
    try:
        dt = datetime.datetime.strptime(raw, DATE_FORMAT)
        return dt.replace(tzinfo=TAIPEI_TZ)
    except Exception:
        return None


def fetch(limit=20):
    """回傳 PTT Stock 板首頁貼文清單，每筆含 title/link/pubdate/body/description/source。"""
    session = _make_session()
    resp = fetch_html(LISTING_URL, session=session)
    if resp is None:
        print("[ptt] 列表頁擷取失敗（over18 cookie 可能失效或被擋），略過此來源")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    entries = soup.select("div.r-ent")
    if not entries:
        print("[ptt] 列表頁未解析到任何貼文，可能頁面結構已變更，略過此來源")
        return []

    articles = []
    for entry in entries[:limit]:
        title_tag = entry.select_one("div.title a")
        if not title_tag:
            continue  # 已刪除文章無連結
        title = title_tag.get_text(strip=True)
        link = title_tag.get("href")
        if link and link.startswith("/"):
            link = "https://www.ptt.cc" + link

        aresp = fetch_html(link, session=session)
        if aresp is None:
            continue
        asoup = BeautifulSoup(aresp.text, "html.parser")
        main = asoup.select_one("#main-content")
        if not main:
            continue

        meta_values = main.select("span.article-meta-value")
        pubdate = _parse_pubdate(meta_values[3].get_text(strip=True)) if len(meta_values) > 3 else None

        for tag in main.select(
            "div.article-metaline, div.article-metaline-right, div.push, "
            "span.f2, div.article-metaline span"
        ):
            tag.decompose()
        body = main.get_text("\n", strip=True)
        # 去除簽名檔分隔線之後的內容（常見 "--" 分隔）
        body = re.split(r"\n--\n", body)[0].strip()

        articles.append(
            {
                "title": title,
                "link": link,
                "pubdate": pubdate,
                "body": body,
                # Revision Round 1（回應 REVIEW.md MAJOR）：見 fetch_cnyes.py
                # 同樣的說明，改傳完整 body，由 summarize.py 統一截斷+加"…"。
                "description": body,
                "source": "ptt",
            }
        )
    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
