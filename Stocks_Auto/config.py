import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 輸出路徑（repo 內相對路徑，使用者之後會自行搬移到 Websites repo）
OUTPUT_DIR = os.path.join(BASE_DIR, "websites", "Stocks", "backend", "data")
FILE_NAME_FORMAT = "%Y-%m-%d.json"

# 排程建議執行時間（v1 手動執行，不做 Task Scheduler 自動化，見 PLAN.md Q5）
SUGGESTED_RUN_TIME = "15:00"

RULES_FILE = os.path.join(BASE_DIR, "rules.md")

# 篩選規則參數（對應 rules.md）
MIN_BODY_LENGTH = 600  # rules.md 規則 01
TODAY_ONLY = True  # rules.md 規則 02

# 財經關鍵字（rules.md 規則 03：YouTube 來源內容需比對，非財經內容當日略過）
FINANCIAL_KEYWORDS = [
    "股市", "台股", "大盤", "財經", "投資", "升息", "降息", "通膨", "匯率",
    "個股", "股價", "上市", "上櫃", "券商", "外資", "法人", "財報", "營收",
    "指數", "殖利率", "美股", "陸股", "期貨", "基金", "央行", "利率",
]

# 去重模組（M4）設定：標題相似度門檻，difflib.SequenceMatcher，範圍 0-1
DEDUP_THRESHOLD = 0.8

# 新聞來源清單（M2）。method: "rss" 或 "html"
SOURCES = {
    "yahoo": {
        "name": "Yahoo奇摩股市",
        "method": "rss",
        "url": "https://tw.stock.yahoo.com/rss?category=news",
        "confirmed": True,  # RESEARCH.md Findings #1：已即時驗證可用
    },
    "cnyes": {
        "name": "鉅亨網",
        "method": "html",
        "url": "https://news.cnyes.com/news/cat/headline",
        "confirmed": False,  # RESEARCH.md Findings #2：無確認可用 RSS，走 HTML 爬蟲
    },
    "udn": {
        "name": "經濟日報",
        "method": "html",
        "url": "https://money.udn.com/money/index",
        "confirmed": False,  # RESEARCH.md Findings #2：舊 RSS 已失效/不明朗，走 HTML 爬蟲
    },
    "ctee": {
        "name": "工商時報",
        "method": "html",
        "url": "https://www.ctee.com.tw/livenews/tw",
        "confirmed": False,  # RESEARCH.md Findings #2：無確認可用 RSS，走 HTML 爬蟲
    },
    "ptt": {
        "name": "PTT Stock板",
        "method": "html",
        "url": "https://www.ptt.cc/bbs/Stock/index.html",
        "confirmed": False,  # RESEARCH.md Findings #4：無 RSS，需 over18 cookie，ToS 灰色地帶
    },
    "youtube": {
        "name": "57東森財經新聞",
        "method": "youtube",
        # RESEARCH.md Findings #8：頻道 handle @57ETFN，channel_id 已交叉驗證
        "channel_id": "UCuzqko_GKcj9922M1gUo__w",
        "rss_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCuzqko_GKcj9922M1gUo__w",
        "confirmed": True,  # 頻道/RSS 已驗證，字幕可用性未知，實作時逐支影片驗證
    },
}

# 台灣證交所(TWSE)/櫃買中心(TPEx) 上市櫃公司代碼對照表（M5 分組）
# RESEARCH.md Findings #6：已直接驗證可下載，欄位含「公司代號」「公司名稱」「公司簡稱」
TWSE_LISTED_CSV = "https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv"
TPEX_LISTED_CSV = "https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv"

# 公司代碼對照表本地快取（避免每次執行都重新下載）
COMPANY_MAP_CACHE = os.path.join(BASE_DIR, "cache", "company_map.json")

# HTTP 請求共用設定
REQUEST_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_HEADERS = {"User-Agent": USER_AGENT}

# 未分類到任何股票代碼的新聞歸入此分組
UNCLASSIFIED_GROUP = "大盤/未分類"
