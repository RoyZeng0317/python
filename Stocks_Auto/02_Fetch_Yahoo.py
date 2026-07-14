import datetime
import email.utils
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

import config

TAIPEI_TZ = datetime.timezone(datetime.timedelta(hours=8))
BOILERPLATE_MARKERS = ["加入為", "熱門來源"]


def _parse_pubdate(raw):
    try:
        dt = email.utils.parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(TAIPEI_TZ)
    except Exception:
        return None


def _fetch_full_body(link):
    try:
        resp = requests.get(link, headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
    except Exception:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    section = soup.select_one("section.module-article-body") or soup.select_one(
        "[class*=article-body]"
    )
    if not section:
        return ""
    paragraphs = []
    for p in section.find_all("p"):
        text = p.get_text(strip=True)
        if not text:
            continue
        if any(marker in text for marker in BOILERPLATE_MARKERS):
            continue
        paragraphs.append(text)
    return "\n".join(paragraphs)


def fetch():
    """回傳 Yahoo奇摩股市 最新新聞清單，每筆含 title/link/pubdate/body/description/source。"""
    src = config.SOURCES["yahoo"]
    try:
        resp = requests.get(src["url"], headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[yahoo] RSS 擷取失敗：{exc}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        print(f"[yahoo] RSS 解析失敗：{exc}")
        return []

    articles = []
    for item in root.findall(".//item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pubdate_el = item.find("pubDate")
        desc_el = item.find("description")

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = (link_el.text or "").strip() if link_el is not None else ""
        description = (desc_el.text or "").strip() if desc_el is not None else ""
        pubdate = _parse_pubdate(pubdate_el.text) if pubdate_el is not None else None

        if not title or not link:
            continue

        body = _fetch_full_body(link)
        if not body:
            # 全文擷取失敗時退回 RSS description，讓文章仍可能通過後續規則判斷
            body = description

        articles.append(
            {
                "title": title,
                "link": link,
                "pubdate": pubdate,
                "body": body,
                "description": description,
                "source": "yahoo",
            }
        )

    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
