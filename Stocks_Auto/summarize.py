"""M6 摘要/彙整模組（PLAN.md Q10 方案B為主 + 方案C輔助，零LLM依賴）。
- 單篇摘要：優先用來源本身的 description（Yahoo RSS 已提供，其餘來源以
  body 前150字代理），依規則截到約100-150字（方案B：標題+首段擷取）。
- 分組關鍵字標籤：對每個分組內所有文章合併文本，用 12_Martix_DataSheet.py
  的 TF-IDF term-document matrix 取前 N 高權重詞作為關鍵字標籤（方案C）。
"""
import importlib

tfidf = importlib.import_module("12_Martix_DataSheet")

SUMMARY_MAX_LEN = 150


def summarize_article(article):
    """回傳單篇摘要文字（100-150字內，規則式擷取，優先用description）。"""
    description = (article.get("description") or "").strip()
    body = (article.get("body") or "").strip()
    text = description or body
    if len(text) > SUMMARY_MAX_LEN:
        text = text[:SUMMARY_MAX_LEN].rstrip() + "…"
    return text


def group_keywords(articles, top_n=5):
    """回傳分組內所有文章合併後的 TF-IDF 關鍵字標籤（跨文章統計，非單篇）。"""
    combined_text = " ".join((a.get("title") or "") + " " + (a.get("body") or "") for a in articles)
    if not combined_text.strip():
        return []
    terms, matrix = tfidf.build_matrix([combined_text])
    return tfidf.top_keywords(0, terms, matrix, top_n=top_n)


def summarize_groups(groups, top_n_keywords=5):
    """輸入 grouping.group() 的輸出，回傳附加摘要與關鍵字標籤後的結構：
    {group_name: {"keywords": [...], "articles": [article_with_summary, ...]}}
    """
    result = {}
    for group_name, articles in groups.items():
        summarized_articles = []
        for article in articles:
            enriched = dict(article)
            enriched["summary"] = summarize_article(article)
            summarized_articles.append(enriched)
        result[group_name] = {
            "keywords": group_keywords(articles, top_n=top_n_keywords),
            "articles": summarized_articles,
        }
    return result


if __name__ == "__main__":
    sample_groups = {
        "2330 台積電": [
            {
                "title": "台積電法說會釋出樂觀展望，外資喊買半導體股",
                "body": "台積電今日舉行法說會，管理層釋出樂觀展望，外資紛紛喊買半導體股，股價應聲上漲。" * 3,
                "description": "台積電法說會釋出樂觀展望，外資喊買半導體股，股價應聲上漲，市場氣氛熱絡。",
                "additional_sources": [],
            }
        ],
        "大盤/未分類": [
            {
                "title": "颱風假各縣市停班停課最新消息一次看",
                "body": "颱風來襲，各縣市政府陸續公布停班停課消息。" * 3,
                "description": "颱風來襲，各縣市政府陸續公布停班停課消息，請民眾注意安全。",
                "additional_sources": [],
            }
        ],
    }
    out = summarize_groups(sample_groups)
    for group_name, data in out.items():
        print(group_name, "keywords=", data["keywords"])
        for a in data["articles"]:
            print("  -", a["title"], "| summary=", a["summary"])
