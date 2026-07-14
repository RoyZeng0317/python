"""M5 分組模組。
下載/快取 TWSE(上市) + TPEx(上櫃) 公司代號/名稱/簡稱對照表
（RESEARCH.md Findings #6，已驗證可下載），對每篇新聞的 title+body 做
公司簡稱/名稱關鍵字比對，歸入對應「代號 簡稱」分組；找不到對應者歸入
config.UNCLASSIFIED_GROUP（大盤/未分類）。同組內再依「重要性」
（additional_sources 數量，即同一事件被幾個來源報導）由多到少排序。

快取：公司對照表變動極少，寫入 config.COMPANY_MAP_CACHE，超過
CACHE_MAX_AGE_DAYS 才重新下載，避免每次執行都打 TWSE 網站。

Revision Round 1 (回應 REVIEW.md BLOCKER)：
「簡稱長度 <= SHORT_KEYWORD_MAX_LEN」的關鍵字（例如「世界」「新建」「大台北」
「中華」「大田」「中石化」「三商」）極容易與常用中文詞、地名、人名子字串碰撞，
造成假陽性分組。REVIEW.md 實際抽查 7 個非顯而易見分組，6/7 為假陽性，且全部
是「關鍵字未出現在標題、只出現在內文某處」的情況。
修法（REVIEW.md 建議 #2，signal-based）：對這類短關鍵字，不再只要 body 內任意
出現一次子字串就算數，而是要求下列任一更強訊號：
  (a) 關鍵字出現在標題（title）中；或
  (b) 關鍵字出現在 body 中，且股票代號數字就出現在該次命中的鄰近文字窗口內
      （代表這是一段「代號+簡稱」同時出現的財經語境，例如報價表、法人買賣超表）。
較長（> SHORT_KEYWORD_MAX_LEN）、較不容易與常用詞碰撞的公司名稱（如台積電、
台塑、華新科）維持原本「body 內任一子字串命中即算數」的行為，不因此修法而降低
可回收率（REVIEW.md 明確指出這些不是問題來源）。

第二類殘留假陽性（本次修法過程中重新驗證時另外發現，屬於同一BLOCKER的延伸）：
即使是「長」公司全名（例如「三商投資控股股份有限公司」，11字，不受上面
SHORT_KEYWORD_MAX_LEN規則影響），仍可能出現在 TWSE/TPEx 統計揭露文字常見的
「不含金融保險業32家及三商投資控股股份有限公司計33家」這種「排除性列舉」子句
裡——文章其實在講全市場營收統計，三商投資控股只是「不算在內」清單裡被列出的
其中一家，不是報導主體。這種句型在真正的公司公告（例如「宏易」更名公告）裡
不會出現，可用「關鍵字前方鄰近『不含/不包括/扣除』+ 後方鄰近『計X家/共X家』」
這個結構訊號辨識並排除，而不需要犧牲其他長名稱在 body 中的正常比對能力。
"""
import csv
import datetime
import io
import json
import os
import re

import requests

import config

CACHE_MAX_AGE_DAYS = 7

# 簡稱長度 <= 這個門檻時，視為「與常用詞/地名/人名碰撞風險高」的短關鍵字，
# 比對時需要更強訊號（標題命中 或 代號鄰近共現），不能只靠 body 任意子字串命中。
# 依 REVIEW.md 實際抽查到的假陽性案例（世界2字/新建2字/大台北3字/中華2字/
# 大田2字/中石化3字/三商2字）皆為 2-3 字，故取 3 作為門檻。
SHORT_KEYWORD_MAX_LEN = 3

# 代號與短簡稱「鄰近共現」時，代號需落在關鍵字命中位置前後這個字元數窗口內
# （涵蓋常見報價表/買賣超表格「代號 簡稱 ... 」或「簡稱(代號)」的排版方式）。
CODE_PROXIMITY_WINDOW = 20

# 「排除性列舉」子句偵測（見上方 module docstring 第二類殘留假陽性）：
# 關鍵字前方鄰近出現這些排除語，且後方鄰近出現「計X家/共X家」彙總計數語，
# 代表這次命中只是統計揭露文字裡「不算在內」清單的一員，非文章報導主體。
EXCLUSION_CLAUSE_MARKERS = ["不含", "不包括", "不計入", "扣除"]
EXCLUSION_CLAUSE_WINDOW = 25
AGGREGATE_COUNT_RE = re.compile(r"[計共]\s*\d+\s*家")

# 第三類殘留假陽性（實跑 2026-07-14 真實資料時再次發現，屬同一 BLOCKER 的延伸）：
# TWSE 官方「公司簡稱」欄位本身有些就直接是通用中文詞彙/地名，例如代號5347
# 「世界先進」的官方簡稱欄位就直接是「世界」兩字、代號1473「台南企業」的官方
# 簡稱就直接是「台南」兩字。「標題命中即視為有效」對這類詞完全不夠，因為它們
# 常常只是被包在一個更大、語意完全無關的常用詞/地名新聞裡（例如「全世界」
# 「世界衛生組織」包含「世界」；「盤點桃園、台南、高雄」包含「台南」），
# 跟對應的股票代號完全無關。這類詞即使命中在標題裡，仍必須通過代號鄰近共現
# 檢查才算數，不能像其他短簡稱一樣「標題命中就直接放行」。
#
# 分兩類收錄：
# (a) 台灣縣市/地區行政區名稱：範圍明確、可窮舉，凡「公司簡稆」剛好等於地名
#     時全部視為高風險（地名新聞極常見，碰撞機率高，這類收錄不會有「漏收」
#     疑慮，因為地名清單本身就是封閉集合）。
# (b) REVIEW.md 或本次實跑驗證中，另外明確發現的「簡稱本身就是通用中文詞彙」
#     案例（世界、新建、中華、大田）。此類無法窮舉，只能隨實際踩到的案例
#     持續累積，屬於本次修法的已知限制（見 BUILD_LOG.md Remaining Known
#     Limitations），不是宣稱「已列舉全部可能碰撞詞」。
_TAIWAN_PLACE_NAMES = {
    "台北", "新北", "桃園", "台中", "台南", "高雄", "基隆", "新竹", "苗栗",
    "彰化", "南投", "雲林", "嘉義", "屏東", "宜蘭", "花蓮", "台東", "澎湖",
    "金門", "連江", "大台北", "大台南", "大高雄", "大台中",
}
# 「三星」：TWSE代號5007「三星科技」的官方簡稱剛好與國際知名品牌 Samsung
# 的中文慣用譯名完全相同，財經新聞裡談南韓三星集團（Samsung Electronics）
# 的頻率遠高於談台灣這家同名小型上市公司，實跑時已驗證誤判（見 BUILD_LOG.md
# Revision Round 1：SK海力士/三星ADR新聞被誤分進「5007 三星」）。
# 「力士」：TWSE代號4923的官方簡稱「力士」剛好是「海力士」(SK Hynix，南韓
# 記憶體大廠)後兩個字的子字串，財經新聞常見「SK海力士」全稱，同一篇實跑時
# 就被誤判進「4923 力士」，與此案例一併記錄、一併修正。
_KNOWN_COMMON_WORD_SHORT_NAMES = {"世界", "新建", "中華", "大田", "三星", "力士"}
COMMON_WORD_COLLISION_KEYWORDS = _TAIWAN_PLACE_NAMES | _KNOWN_COMMON_WORD_SHORT_NAMES


def _download_csv(url):
    resp = requests.get(url, headers=config.REQUEST_HEADERS, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    resp.encoding = "utf-8-sig"
    reader = csv.DictReader(io.StringIO(resp.text))
    rows = []
    for row in reader:
        code = (row.get("公司代號") or "").strip()
        name = (row.get("公司名稱") or "").strip()
        short = (row.get("公司簡稱") or "").strip()
        if code and (name or short):
            rows.append({"code": code, "name": name, "short": short})
    return rows


def _load_company_list():
    cache_path = config.COMPANY_MAP_CACHE
    if os.path.exists(cache_path):
        age_days = (
            datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cache_path))
        ).days
        if age_days < CACHE_MAX_AGE_DAYS:
            try:
                with open(cache_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass  # 快取損毀則重新下載

    companies = []
    for url in (config.TWSE_LISTED_CSV, config.TPEX_LISTED_CSV):
        try:
            companies.extend(_download_csv(url))
        except Exception as exc:
            print(f"[grouping] 下載公司對照表失敗 {url}: {exc}")

    if companies:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(companies, f, ensure_ascii=False)
    return companies


def _build_lookup(companies):
    """回傳依「簡稱長度由長到短」排序的 (keyword, code, display_name) 清單，
    比對時優先匹配較長的簡稱，避免短簡稱誤配（例如「台泥」不會被更短的字串誤蓋）。"""
    lookup = []
    seen = set()
    for c in companies:
        for keyword in filter(None, [c["short"], c["name"]]):
            key = (keyword, c["code"])
            if key in seen or len(keyword) < 2:
                continue
            seen.add(key)
            display = f"{c['code']} {c['short'] or c['name']}"
            lookup.append((keyword, c["code"], display))
    lookup.sort(key=lambda t: len(t[0]), reverse=True)
    return lookup


def _is_exclusion_clause_occurrence(text, idx, keyword):
    """判斷 text 中位於 idx 的這次 keyword 命中，是否落在「不含...計X家」這種
    統計揭露排除性子句內（見 module docstring 第二類殘留假陽性）。"""
    before = text[max(0, idx - EXCLUSION_CLAUSE_WINDOW):idx]
    after = text[idx + len(keyword): idx + len(keyword) + EXCLUSION_CLAUSE_WINDOW]
    return any(m in before for m in EXCLUSION_CLAUSE_MARKERS) and bool(AGGREGATE_COUNT_RE.search(after))


def _code_near(text, idx, keyword, code):
    """code 是否出現在 idx 這次命中位置前後 CODE_PROXIMITY_WINDOW 字元窗口內。
    代理「代號+簡稱同時出現」的財經語境（報價表、法人買賣超表等）。"""
    if not code:
        return False
    window_start = max(0, idx - CODE_PROXIMITY_WINDOW)
    window_end = idx + len(keyword) + CODE_PROXIMITY_WINDOW
    return code in text[window_start:window_end]


def _has_valid_match(keyword, code, title, text):
    """判斷 keyword 是否在這篇文章裡有「有效」命中：
    1. 標題命中且不屬於 COMMON_WORD_COLLISION_KEYWORDS：直接視為有效
       （headline 直接點名，訊號最強，不需要額外檢查）。
    2. 其餘情況（body 命中，或標題命中但屬於常用詞碰撞清單）：逐一檢查每次
       出現位置（在 title+body 合併後的 text 裡搜尋）——
       a. 先排除「排除性列舉子句」命中（無論關鍵字長短，見第二類假陽性）；
       b. 通過 a 後，若關鍵字長度 <= SHORT_KEYWORD_MAX_LEN 或屬於常用詞碰撞
          清單，還需要股票代號在該次命中附近共現才算數；其餘長度較長、較不
          易誤判的名稱則此次出現即視為有效。
    只要找到一次有效命中就回傳 True；全部出現位置都無效才回傳 False。
    """
    is_collision_prone = keyword in COMMON_WORD_COLLISION_KEYWORDS
    if keyword in title and not is_collision_prone:
        return True

    start = 0
    require_code_proximity = len(keyword) <= SHORT_KEYWORD_MAX_LEN or is_collision_prone
    while True:
        idx = text.find(keyword, start)
        if idx == -1:
            return False
        if not _is_exclusion_clause_occurrence(text, idx, keyword):
            if not require_code_proximity or _code_near(text, idx, keyword, code):
                return True
        start = idx + 1


def group(articles, companies=None):
    """回傳 dict：{分組顯示名稱: [articles...]}，組內依 additional_sources 數量（重要性）由多到少排序。"""
    companies = companies if companies is not None else _load_company_list()
    lookup = _build_lookup(companies)

    groups = {}
    for article in articles:
        title = article.get("title") or ""
        text = title + " " + (article.get("body") or "")
        matched_display = None
        matched_keyword = None
        for keyword, code, display in lookup:
            if _has_valid_match(keyword, code, title, text):
                matched_display = display
                matched_keyword = keyword
                break
        group_name = matched_display or config.UNCLASSIFIED_GROUP
        # 附加比對理由於文章物件上，僅供驗證/除錯使用；output.py 序列化時不會
        # 輸出這個欄位（_serialize_article 只挑選白名單欄位），不影響最終JSON schema。
        article["_match_keyword"] = matched_keyword
        groups.setdefault(group_name, []).append(article)

    for group_name, group_articles in groups.items():
        group_articles.sort(
            key=lambda a: len(a.get("additional_sources") or []), reverse=True
        )

    return groups


if __name__ == "__main__":
    companies = _load_company_list()
    print(f"公司對照表筆數: {len(companies)}")
    sample = [
        {"title": "台積電法說會釋出樂觀展望，外資喊買半導體股", "body": "", "additional_sources": [1, 2]},
        {"title": "颱風假各縣市停班停課最新消息一次看", "body": "", "additional_sources": []},
    ]
    result = group(sample, companies)
    for group_name, arts in result.items():
        print(group_name, "->", [a["title"] for a in arts])
