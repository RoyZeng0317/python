"""M2 擷取器：YouTube（57東森財經新聞頻道）。
RESEARCH.md Findings #8：頻道RSS已驗證可用，抓當日最新影片清單；
但頻道內容混雜社會/國際新聞，故先套用 rules.py 的財經關鍵字比對（rules.md 規則03）
篩掉非財經標題，再對通過篩選的影片嘗試抓字幕。

已知限制（見 BUILD_LOG.md）：實測 2026-07-14 當天最新 15 支影片，
`YouTubeTranscriptApi.list()` 全數回傳 TranscriptsDisabled（該頻道未提供字幕），
代表本來源目前實際上抓不到任何內文，僅能拿到「標題+發布時間」。
依 Q6 拍板 fallback：無字幕時標記「略過」但不中斷整體流程，本模組對每支
無字幕影片略過（不產出 article），若全數略過則回傳空清單，由 pipeline 端優雅跳過。
"""
import datetime
import xml.etree.ElementTree as ET

import requests

import config

ATOM_NS = "http://www.w3.org/2005/Atom"
YT_NS = "http://www.youtube.com/xml/schemas/2015"
NS = {"atom": ATOM_NS, "yt": YT_NS}


def _financial_title_ok(title):
    return any(keyword in title for keyword in config.FINANCIAL_KEYWORDS)


def _fetch_transcript_text(video_id):
    """嘗試抓字幕文字；抓不到（TranscriptsDisabled/NoTranscriptFound/被擋等）回傳 None。"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        return None
    try:
        api = YouTubeTranscriptApi()
        result = api.fetch(video_id, languages=["zh-Hant", "zh-TW", "zh", "en"])
        snippets = result.snippets if hasattr(result, "snippets") else result
        return "".join(s.text for s in snippets)
    except Exception as exc:
        print(f"[youtube] {video_id} 無法取得字幕（略過，不中斷流程）：{type(exc).__name__}")
        return None


def fetch(limit=15):
    """回傳頻道當日最新影片清單（僅含財經關鍵字比對通過且成功取得字幕者）。"""
    src = config.SOURCES["youtube"]
    try:
        resp = requests.get(src["rss_url"], headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[youtube] 頻道 RSS 擷取失敗：{exc}")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError as exc:
        print(f"[youtube] 頻道 RSS 解析失敗：{exc}")
        return []

    entries = root.findall("atom:entry", NS)[:limit]
    articles = []
    skipped_non_financial = 0
    skipped_no_transcript = 0

    for entry in entries:
        video_id_el = entry.find("yt:videoId", NS)
        title_el = entry.find("atom:title", NS)
        published_el = entry.find("atom:published", NS)
        if video_id_el is None or title_el is None:
            continue
        video_id = video_id_el.text
        title = title_el.text or ""

        if not _financial_title_ok(title):
            skipped_non_financial += 1
            continue

        pubdate = None
        if published_el is not None and published_el.text:
            try:
                pubdate = datetime.datetime.fromisoformat(
                    published_el.text.replace("Z", "+00:00")
                ).astimezone(datetime.timezone(datetime.timedelta(hours=8)))
            except Exception:
                pubdate = None

        transcript = _fetch_transcript_text(video_id)
        if not transcript:
            skipped_no_transcript += 1
            continue

        link = f"https://www.youtube.com/watch?v={video_id}"
        articles.append(
            {
                "title": title,
                "link": link,
                "pubdate": pubdate,
                "body": transcript,
                # Revision Round 1（回應 REVIEW.md MAJOR）：見 fetch_cnyes.py
                # 同樣的說明，改傳完整 transcript，由 summarize.py 統一截斷+加"…"。
                "description": transcript,
                "source": "youtube",
            }
        )

    print(
        f"[youtube] 共{len(entries)}支影片，財經關鍵字未過{skipped_non_financial}支，"
        f"無字幕略過{skipped_no_transcript}支，成功{len(articles)}支"
    )
    return articles


if __name__ == "__main__":
    result = fetch()
    print(f"取得 {len(result)} 篇")
    for a in result[:3]:
        print("-", a["title"], "| body_len=", len(a["body"]), "| pubdate=", a["pubdate"])
