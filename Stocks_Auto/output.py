"""M7 報告輸出模組。
將 summarize.summarize_groups() 的結果組成 JSON，寫到
config.OUTPUT_DIR / <today>.json（檔名格式 config.FILE_NAME_FORMAT）。
僅輸出 JSON（PLAN.md Q4：先不做 Markdown/HTML）。
"""
import datetime
import json
import os

import config


def _serialize_article(article):
    """將 article dict 轉為可 json.dump 的形式（pubdate -> ISO字串，移除大型 body 只留 summary）。"""
    pubdate = article.get("pubdate")
    pubdate_str = pubdate.isoformat() if isinstance(pubdate, datetime.datetime) else None
    return {
        "title": article.get("title"),
        "link": article.get("link"),
        "source": article.get("source"),
        "pubdate": pubdate_str,
        "summary": article.get("summary"),
        "additional_sources": article.get("additional_sources", []),
    }


def build_report(summarized_groups, report_date=None):
    report_date = report_date or datetime.date.today()
    groups_out = []
    for group_name, data in summarized_groups.items():
        articles = data["articles"]
        groups_out.append(
            {
                "group": group_name,
                "keywords": data["keywords"],
                "article_count": len(articles),
                "articles": [_serialize_article(a) for a in articles],
            }
        )
    # 分組排序：文章數量多的分組排前面（貼合「總整理快速瀏覽」情境），大盤/未分類固定排最後
    groups_out.sort(
        key=lambda g: (g["group"] == config.UNCLASSIFIED_GROUP, -g["article_count"])
    )
    return {
        "date": report_date.isoformat(),
        "generated_at": datetime.datetime.now().isoformat(),
        "group_count": len(groups_out),
        "total_articles": sum(g["article_count"] for g in groups_out),
        "groups": groups_out,
    }


def write_report(report, output_dir=None, filename_format=None):
    output_dir = output_dir or config.OUTPUT_DIR
    filename_format = filename_format or config.FILE_NAME_FORMAT
    os.makedirs(output_dir, exist_ok=True)

    report_date = datetime.date.fromisoformat(report["date"])
    filename = report_date.strftime(filename_format)
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


if __name__ == "__main__":
    sample_summarized_groups = {
        "2330 台積電": {
            "keywords": ["台積", "半導", "外資"],
            "articles": [
                {
                    "title": "台積電法說會釋出樂觀展望",
                    "link": "https://example.com/1",
                    "source": "yahoo",
                    "pubdate": datetime.datetime.now(),
                    "summary": "台積電法說會釋出樂觀展望，外資喊買半導體股。",
                    "additional_sources": [],
                }
            ],
        }
    }
    report = build_report(sample_summarized_groups)
    path = write_report(report)
    print("已輸出：", path)
