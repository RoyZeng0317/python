"""M4 去重模組。
同日新聞依標題相似度（difflib.SequenceMatcher）判斷是否為同一則新聞的重複報導，
門檻取自 config.DEDUP_THRESHOLD（預設0.8，見 PLAN.md Q7）。
合併時保留「涵蓋內容最多者」（body最長者，best-effort代理『報導最完整』）為代表，
其餘列為 additional_sources 附上來源與連結。

Revision Round 1（回應 REVIEW.md MAJOR）：
純標題相似度會誤判「格式相同、報導主體不同」的文章為重複，實際案例：
「[情報] 0714 上市投信買賣超排行」vs「[情報] 0714 上市外資買賣超排行」
標題相似度 0.8947（>= 0.8 門檻），但一篇談投信一篇談外資，是兩份不同資料，
合併會讓其中一篇的內容從輸出中消失。
修法（REVIEW.md 建議）：標題相似度達門檻後，還需通過兩個額外檢查才真正合併：
  1. 「區辨詞」否決規則：若兩標題分別命中同一組「區辨詞」（例如 外資/投信/
     自營商）裡的不同詞，視為報導不同主體，直接否決合併，不論標題相似度多高。
  2. body 內容相似度（字元 bigram Jaccard）也要達到寬鬆門檻，用來擋「標題結構
     幾乎相同但內文主體完全不同」的一般情況，不只依賴人工列出的區辨詞清單。
"""
from difflib import SequenceMatcher

import config

# 區辨詞組：同一組內任兩個詞若分別出現在兩篇標題中，視為報導不同主體，否決合併。
# 目前只收錄 REVIEW.md 實際發現、且屬於「格式相同、常見於財經情報類標題」的
# 買賣超三大法人分類，避免過度擴張造成漏合併風險。
DISTINGUISHING_TERM_GROUPS = [
    {"外資", "投信", "自營商"},
]

# body 內容相似度（字元 bigram Jaccard）門檻：刻意設得寬鬆，只用來擋「標題相似
# 但內文主體幾乎無重疊」的極端情況，不影響同事件被不同來源以不同措辭報導、
# 但確實談同一件事的正常合併（見 BUILD_LOG.md 正面控制組測試）。
BODY_SIMILARITY_MIN = 0.15
BODY_SHINGLE_LEN = 2
BODY_COMPARE_CHARS = 400


def _title_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def _distinguishing_conflict(title_a, title_b):
    """若兩標題分別命中同一組區辨詞裡的不同詞，回傳 True（否決合併）。"""
    for group in DISTINGUISHING_TERM_GROUPS:
        terms_a = {t for t in group if t in title_a}
        terms_b = {t for t in group if t in title_b}
        if terms_a and terms_b and terms_a.isdisjoint(terms_b):
            return True
    return False


def _char_shingles(text, n=BODY_SHINGLE_LEN):
    text = (text or "")[:BODY_COMPARE_CHARS]
    if len(text) < n:
        return set()
    return {text[i:i + n] for i in range(len(text) - n + 1)}


def _body_similarity(body_a, body_b):
    """字元 bigram Jaccard 相似度；任一方沒有 body 可比對時，視為「無法用
    body 佐證」，保守起見不當作否決訊號（回傳 1.0，交由標題相似度與區辨詞
    規則決定），避免因為某來源 body 擷取失敗就錯誤地阻擋正常合併。"""
    sa, sb = _char_shingles(body_a), _char_shingles(body_b)
    if not sa or not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def _should_merge(article, rep, threshold):
    title_a, title_b = article["title"], rep["title"]
    if _title_similarity(title_a, title_b) < threshold:
        return False
    if _distinguishing_conflict(title_a, title_b):
        return False
    if _body_similarity(article.get("body"), rep.get("body")) < BODY_SIMILARITY_MIN:
        return False
    return True


def _pick_representative(cluster):
    """群內選一篇代表：body 最長者優先（代理『報導最完整/涵蓋最多』）。"""
    return max(cluster, key=lambda article: len(article.get("body") or ""))


def dedup(articles, threshold=None):
    """對輸入的文章清單做標題相似度去重，回傳去重後清單。
    每篇代表文章新增 `additional_sources` 欄位（list of {source, link, title}）。
    未被合併者 additional_sources 為空 list。
    """
    threshold = threshold if threshold is not None else config.DEDUP_THRESHOLD

    clusters = []  # list of list[article]
    for article in articles:
        placed = False
        for cluster in clusters:
            if _should_merge(article, cluster[0], threshold):
                cluster.append(article)
                placed = True
                break
        if not placed:
            clusters.append([article])

    result = []
    for cluster in clusters:
        rep = dict(_pick_representative(cluster))
        others = [a for a in cluster if a is not rep and a.get("link") != rep.get("link")]
        rep["additional_sources"] = [
            {"source": a.get("source"), "link": a.get("link"), "title": a.get("title")}
            for a in others
        ]
        result.append(rep)
    return result


if __name__ == "__main__":
    # 原始樣本：同事件不同來源用字略異的標題（正面控制組，應合併），
    # 加上一則完全不相關的新聞（不應合併）。
    sample = [
        {"title": "台積電法說會釋出樂觀展望，外資喊買半導體股", "body": "x" * 700, "source": "yahoo", "link": "a1"},
        {"title": "台積電法說會釋出樂觀展望 外資喊買半導體股", "body": "x" * 900, "source": "cnyes", "link": "a2"},
        {"title": "颱風假各縣市停班停課最新消息一次看", "body": "y" * 650, "source": "udn", "link": "a3"},
    ]
    out = dedup(sample)
    print(f"[樣本1: 基本案例] 輸入 {len(sample)} 篇，去重後 {len(out)} 篇")
    for a in out:
        print("-", a["title"], "| source=", a["source"], "| additional=", a["additional_sources"])
    assert len(out) == 2, "台積電兩篇應合併為1、颱風假應獨立成1，共應為2篇"

    # Revision Round 1 迴歸測試 1（負面案例，REVIEW.md 實際發現的誤合併）：
    # 「上市投信買賣超排行」vs「上市外資買賣超排行」標題相似度 0.8947 (>=0.8)，
    # 但內容主體不同（投信 vs 外資），body 內容也幾乎不重疊，不應合併。
    inv_trust_body = "證券代號　證券名稱　買超張數\n2330　台積電　1234\n投信買超前十名如下：..." * 3
    foreign_body = "證券代號　證券名稱　賣超張數\n2454　聯發科　5678\n外資賣超前十名如下：..." * 3
    trust_vs_foreign = [
        {"title": "[情報] 0714 上市投信買賣超排行", "body": inv_trust_body, "source": "ptt", "link": "b1"},
        {"title": "[情報] 0714 上市外資買賣超排行", "body": foreign_body, "source": "ptt", "link": "b2"},
    ]
    title_sim = _title_similarity(trust_vs_foreign[0]["title"], trust_vs_foreign[1]["title"])
    out2 = dedup(trust_vs_foreign)
    print(f"\n[樣本2: 投信vs外資 迴歸測試] 標題相似度={title_sim:.4f}，輸入2篇，去重後 {len(out2)} 篇")
    for a in out2:
        print("-", a["title"], "| additional=", a["additional_sources"])
    assert title_sim >= config.DEDUP_THRESHOLD, "此測試前提是標題相似度需先達門檻，否則沒有測到區辨詞規則"
    assert len(out2) == 2, "投信/外資為不同主體，不應被合併（REVIEW.md BLOCKER案例回歸測試）"

    # Revision Round 1 迴歸測試 2（正面控制組）：同一事件被兩個不同來源報導，
    # 標題幾乎相同、body 內容也高度重疊（近乎轉載），驗證修法後「真正的重複」
    # 仍然能正常合併，而不是把 dedup 整個關掉。
    same_event_body = (
        "京元電子今日召開法說會，公司表示受惠於IC測試需求回溫，"
        "第三季營收展望樂觀，法人預估毛利率將較上季提升，股價應聲上漲逾3%。"
    ) * 4
    genuine_duplicate = [
        {"title": "京元電子法說會展望樂觀 法人喊買", "body": same_event_body, "source": "cnyes", "link": "c1"},
        {"title": "京元電子法說會展望樂觀，法人喊買", "body": same_event_body, "source": "udn", "link": "c2"},
    ]
    out3 = dedup(genuine_duplicate)
    print(f"\n[樣本3: 正面控制組 同事件不同來源] 輸入2篇，去重後 {len(out3)} 篇")
    for a in out3:
        print("-", a["title"], "| additional=", a["additional_sources"])
    assert len(out3) == 1, "同一事件、標題近乎相同且內文高度重疊，修法後仍應合併，證明未把dedup整個關掉"

    print("\n全部 dedup.py 迴歸測試通過。")
