# RESEARCH

## Findings

### 1. Yahoo奇摩股市 RSS 可用性
**答案**：有官方 RSS，且**已即時驗證可用**。已抓取 `https://tw.stock.yahoo.com/rss?category=news` 並取得當下（2026-07-14）真實新聞項目，格式為標準 RSS 2.0，含 `title`/`link`/`pubDate`/`description`（description 即為首段/摘要文字，可直接用於 Q10 的「標題+首段100-150字」方案，甚至可能不需要再另外爬內文頁）。
其他可用分類 feed（來自 RSS 索引頁 `https://tw.stock.yahoo.com/rss-index`）：
- 最新新聞 `https://tw.stock.yahoo.com/rss?category=news`
- 台股要聞 `https://tw.stock.yahoo.com/rss?category=tw-market`
- 國際財經 `https://tw.stock.yahoo.com/rss?category=intl-markets`
- 理財 `https://tw.stock.yahoo.com/rss?category=personal-finance`
- 基金 `https://tw.stock.yahoo.com/rss?category=funds-news`
- 專欄 `https://tw.stock.yahoo.com/rss?category=column`
- 研究報告 `https://tw.stock.yahoo.com/rss?category=research`
- 亦支援自訂：可用股票代碼或關鍵字組出個股/主題 feed（M5分組若想用官方個股feed可考慮，但目前已拍板為「全市場」，此為備註非必要）。
**來源**：`https://tw.stock.yahoo.com/rss-index`（Wayback/即時頁面）+ 實際 WebFetch 驗證 `https://tw.stock.yahoo.com/rss?category=news` 回傳有效內容。
**信心 [High]**：已直接抓取到真實、當下時間戳的 RSS 內容，非僅憑搜尋結果推測。

### 2. 鉅亨網(cnyes)、經濟日報(udn)、工商時報(ctee) 是否提供 RSS
**答案**：**三者目前皆找不到可用的官方 RSS feed**，與 PLAN.md 原先「有 RSS 就用 RSS」的假設不完全成立，需要修正 M2 的策略。細節：
- **鉅亨網 cnyes**：查到的候選 URL（`news.cnyes.com/rss/cat/tw_stock`、`www.cnyes.com/promote/announce/GetRss.ashx`）皆回傳 404。直接檢視 `news.cnyes.com/news/cat/headline` 首頁原始碼，未發現 `<link rel="alternate" type="application/rss+xml">` 或任何 RSS 相關字樣。**結論：無官方RSS，須改用 HTML 爬蟲。**
- **經濟日報 (money.udn.com / edn.udn.com)**：舊版 RSS 服務頁 `http://edn.udn.com/rss.jsp` 已 301 導向到 `https://money.udn.com/money/index`（一般新聞首頁，非RSS），顯示舊RSS服務可能已停用或整併。另一候選 `https://money.udn.com/rssfeed/lists/1001` 可正常開啟，但內容是一般新聞列表頁而非XML feed，頁面本身也未曝露明確的 `.xml` RSS 連結。**結論：官方RSS狀態不明朗/疑似已停用，須改用 HTML 爬蟲，且需人工用瀏覽器再確認一次（有可能該頁面deep link才是真正RSS但WebFetch工具把XML誤判成HTML呈現）。**
- **工商時報 (ctee.com.tw)**：`https://www.ctee.com.tw/rss` 回傳 404；直接檢視首頁原始碼未發現RSS `<link>` 標籤或RSS關鍵字。Feedspot「Top 15 Taiwan News RSS Feeds」清單中雖列出 ctee.com.tw 為第15項，但未能取得其實際 feed URL 細節。**結論：找不到可確認有效的RSS，須改用 HTML 爬蟲，且不排除 feedspot 清單上的舊連結已失效。**
- **robots.txt / ToS**：本次研究未特別針對 cnyes/udn/ctee 的 robots.txt 逐一檢查（PLAN原問題聚焦RSS+ToS，重點先確認RSS有無）；若 Builder 決定改用 HTML 爬蟲，**建議在 M2 開工前先各自檢查一次 `https://www.cnyes.com/robots.txt`、`https://money.udn.com/robots.txt`、`https://www.ctee.com.tw/robots.txt` 的 Disallow 規則**，本研究未涵蓋此步驟，是明確的待補項。
**來源**：直接 WebFetch 多個候選 URL 取得的 404/redirect 結果 + 首頁原始碼檢視 + WebSearch 搜尋結果交叉比對。
**信心 [Medium]**：「找不到」不等於「絕對不存在」——不排除有更隱密的 feed 路徑（例如需要從瀏覽器開發者工具觀察實際載入的 XHR）未被搜尋到；但以目前合理努力（查官方RSS索引頁、首頁meta標籤、社群RSS清單、常見URL pattern）皆未找到，判斷三者短期內不可視為「有現成RSS可直接用」。

### 3. `youtube-transcript-api` 在 2026 年是否仍可正常運作
**答案**：套件仍在維護中（PyPI 最新版本 **1.2.4，發布於 2026-01-29**），但**明確存在 YouTube 端反爬蟲風險**：
- 官方文件本身即說明 YouTube 已開始封鎖已知屬於雲端服務商（AWS/GCP/Azure）的IP，會回傳 `IpBlocked`/`RequestBlocked` 錯誤。
- 社群回報（GitHub issues #511, #593, 2026年討論串）指出需要**住宅代理(residential proxy)輪替**才能穩定繞過封鎖，單純本機/家用網路IP的請求量若不高，風險相對較低，但仍非保證。
- 另有一項**新增風險**（本研究確認度較低，列為需追蹤項）：YouTube 於 2025–2026 導入 **PoToken**（proof-of-origin token）機制作為新一代反機器人手段；截至查詢當下，該套件社群對 PoToken 的支援「仍在開發中 (actively in development)」，代表**未來可能出現目前能跑、但突然失效的情況**。
- 草稿中固定影片ID `1I2iq41Akmo` 是否為一般影片或直播錄影、其內部時間軸是否有對應現實時間的meta資料可用於擷取「09:00-13:00」區間——**本研究無法在不實際呼叫 API/檢視該影片的情況下確認**，且該影片ID已被 Q6 決策取代（改為每天自動抓東森財經新聞頻道當日最新影片），此問題本身可能已因需求變更而過時，但字幕timestamp對應現實時間的機制仍是通用未知數，需 Builder 在 M2 實作時對「當天真實抓到的那支影片」做一次性驗證。
**來源**：`https://pypi.org/project/youtube-transcript-api/`（版本/日期）、`https://github.com/jdepoix/youtube-transcript-api/issues/511`、`/issues/593`（社群反爬蟲討論）。
**信心 [Medium]**：套件本身「存在且仍更新」是 [High] 信心（直接查證PyPI）；但「能否在 Builder 實際跑的當下順利拿到字幕而不被擋」是 [Low] 信心，因為 YouTube 反爬蟲策略會隨時間變化且無法脫離實際執行環境模擬。**What WOULD verify it**：Builder 在 M2 開發時，直接對一支東森財經新聞頻道的近期影片ID跑一次 `YouTubeTranscriptApi.get_transcript()`，實測是否成功、是否需要代理；並準備好 Q6 已拍板的 fallback（無字幕/被擋時標記「略過」但不中斷流程）。

### 4. PTT Stock板 可程式化存取的管道 / over18 / robots.txt / 反爬蟲
**答案**：
- **robots.txt**：直接請求 `https://www.ptt.cc/robots.txt`（嘗試兩次，含 http/https）皆回傳 **404**，代表 PTT **沒有設置 robots.txt 檔案**。無 robots.txt 不等於「歡迎爬蟲」，只是沒有機器可讀的規則可依循；**沒有官方 ToS 明文允許自動化定期抓取**。
- **RSS**：查無 PTT Stock 板官方 RSS feed（PLAN.md 本身也已註記「通常沒有RSS」，本研究確認此假設成立，未找到反例）。
- **over18 驗證機制**：業界（多個公開 GitHub 專案，如 `kuo23/PTT-Stock`、多篇教學文章）採用的共同作法是對請求設定 cookie `over18=1`，即可繞過網頁版的18禁確認頁，此為**成熟且廣泛驗證過的技術手段**，非新風險。
- **反爬蟲機制**：無官方公告的明確反爬蟲規則，但依 PTT 的歷史經驗與一般網站防護常識，**高頻率請求存在被暫時性 429/連線拒絕的風險**（本次研究對 PTT 站本身未實測出429，因為只呼叫了robots.txt端點，非文章列表端點，故無法百分之百確認 Stock 板文章列表的即時限流狀況）。
**來源**：直接 WebFetch `ptt.cc/robots.txt`（404）；WebSearch 多篇PTT爬蟲教學/開源專案交叉確認 over18 cookie 作法；PLAN.md 既有敘述。
**信心 [Medium]**：over18 cookie 繞過機制信心 [High]（大量公開案例一致）；「沒有robots.txt=可安全長期自動化抓取」的推論信心僅 [Medium/Low]，因為**沒有明文允許≠有法律/服務條款上的許可**，且PLAN.md已將此列為使用者需知悉的風險（若不可行需回報使用者而非靜默跳過）——本研究判斷**技術上可行**，但**是否要真的做**仍是政策/風險承受度問題，非純技術問題，建議在 Builder 開工前提醒使用者一次「PTT無官方許可，屬灰色地帶自行承擔」。

### 5. Windows Task Scheduler (`schtasks`) 搭配 venv Python 最佳實務
**答案**：業界慣用做法（多篇教學文章一致）：
1. 不要讓 Task Scheduler 直接指向 `venv\Scripts\python.exe` 執行 .py 檔並依賴預設工作目錄——**務必額外用一個 `.bat` 批次檔包裝**，內容如：
   ```
   @echo off
   cd /d "C:\path\to\project"
   call "C:\path\to\project\venv\Scripts\activate.bat"
   python "C:\path\to\project\run.py"
   ```
   或直接呼叫 venv 內的 `python.exe`/`pythonw.exe` 完整路徑，不透過 activate（更穩定，避免 activate.bat 在非互動式環境下偶發問題）。
2. 若不想跳出黑色主控台視窗，改用 venv 內的 **`pythonw.exe`**（無主控台視窗版本）取代 `python.exe`。
3. Task Scheduler 建立時務必填寫「**起始位置(Start in)**」為專案目錄，否則腳本內的相對路徑會失敗（這點與 M1「改用相對路徑」的規劃直接相關，需注意：相對路徑要嘛靠腳本內部自行 `os.path.dirname(__file__)` 運算絕對化，要嘛依賴 Start in 設定，兩者擇一但不能都不做）。
4. 命令列建立範例：`schtasks /Create /SC DAILY /TN "StocksAutoDaily" /TR "C:\path\to\project\run.bat" /ST 15:00 /RL HIGHEST /F`
5. **已知限制**：Task Scheduler 不會像某些排程系統一樣特別處理 Python 例外/非0 exit code——腳本崩潰時 Task Scheduler 本身不會明顯告警，**建議腳本自行寫 log 檔並在崩潰時寫入錯誤訊息**，否則使用者不會發現排程其實沒有真的產出當天檔案。
**來源**：`https://nihad.hashnode.dev/automate-python-script-using-task-scheduler-on-windows-machine`、`https://codinglap.com/how-to-schedule-a-python-script-in-windows-task-scheduler/`、`https://siddharthshanker.com/blog/programming/python/schedule-automate-python-job-using-windows-task-scheduler/`。
**信心 [High]**：多篇獨立文章結論一致，且與筆者對 Windows Task Scheduler 常見陷阱的既有認知吻合；**但此為v1 stop condition排除的範圍**（PLAN.md已載明Q5未拍板、M8可延後至v1之後），故此為「先備而不用」的資訊。

### 6. TWSE/TPEx 上市櫃公司代碼↔名稱對照表公開資料源
**答案**：**有，且已直接驗證兩個 CSV 端點皆可成功下載、格式清楚可用**：
- **上市 (TWSE)**：`https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv` — 已實際抓取，欄位含「公司代號」「公司名稱」「公司簡稱」（如 1101/臺灣水泥股份有限公司/台泥）等約20+欄位，公司簡稱欄位即為新聞標題比對最實用的欄位。
- **上櫃 (TPEx)**：`https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv` — 已實際抓取，欄位結構相同（公司代號/公司名稱/公司簡稱），資料屬於上櫃公司（如 1240 茂生農經、1259 安心食品服務等）。
- 補充：政府資料開放平台亦有對應資料集頁面 `https://data.gov.tw/dataset/18419`（上市）與 `https://data.gov.tw/dataset/25036`（上櫃），可作為除了 mopsfin 直連CSV外的備援/說明來源；另有 TWSE OpenAPI（`https://openapi.twse.com.tw/`）與 TPEx OpenAPI（`https://www.tpex.org.tw/openapi/`）提供 Swagger 文件化的 API，若未來需要更即時的資料可轉用。
**來源**：直接 WebFetch 兩個 CSV URL 成功取得內容；`https://data.gov.tw/dataset/18419`、`https://data.gov.tw/dataset/25036`、`https://openapi.twse.com.tw/`、`https://www.tpex.org.tw/openapi/`（WebSearch交叉確認）。
**信心 [High]**：兩個CSV端點皆已實際成功下載並確認欄位內容，非僅憑搜尋結果推測。

### 7. jieba vs CKIP Tagger（Windows環境安裝難易度與效能，供M6 v2參考）
**答案**：
- **準確度**：CKIP Tagger 在 ASBC 4.0 語料庫（5萬句）測試中斷詞準確率約 97.49%，優於 jieba 的 90.51%；CKIP對繁體中文/台灣用語（如「長照」視為一詞）處理較貼合本地語境，jieba 原生針對簡體中文/中國大陸用語設計，繁中支援是後加的，對台灣特有詞彙較容易切錯。
- **安裝難易度（Windows）**：本次研究未找到針對 Windows 平台安裝步驟的第一手實測資料（搜尋結果多為功能比較文，非安裝踩雷紀錄）。一般認知（[Low]信心，非本次驗證）：jieba 是純Python套件、`pip install jieba` 即可，幾乎無額外依賴，Windows安裝容易；CKIP Tagger 底層依賴 TensorFlow 並需下載額外模型檔（數百MB～GB等級），安裝與首次執行的下載/初始化較繁瑙，且與新版TensorFlow/Python版本相容性需留意（CKIP Tagger專案更新頻率較低）。**此為[Low]信心的一般性認知，建議M6若真的要導入v2 TextRank時，Builder自行在目標Windows機器上實測安裝一次以確認，而非採信本研究的間接推論。**
**來源**：`https://ithelp.ithome.com.tw/articles/10272895`（Jieba vs CKIP 語料庫比較）、`https://medium.com/中文-nlp-處理/繁體中文斷詞使用者字典引用比較...`系列文章。
**信心 [Medium]**（準確度數據部分，來自具體引用的語料庫測試數字）/ **[Low]**（Windows安裝難易度部分，未實測，屬一般性推論）。此項目為 v2 選配（M6方案A待Q10/使用者反饋後才啟用），非v1阻塞項，優先度低。

### 8. 東森財經新聞 YouTube 頻道確認（新增問題）
**答案**：
1. **頻道 handle / URL**：`https://www.youtube.com/@57ETFN`（頻道顯示名稱「57東森財經新聞」）。
2. **頻道ID (UC...)**：`UCuzqko_GKcj9922M1gUo__w` —— **已交叉驗證兩次**：(a) WebSearch結果中 vidIQ 統計頁面 URL 含有此ID (`vidiq.com/youtube-stats/channel/UCuzqko_GKcj9922M1gUo__w/`)，(b) 直接對 `https://www.youtube.com/feeds/videos.xml?channel_id=UCuzqko_GKcj9922M1gUo__w` 發出請求，**成功取得真實RSS內容**，feed中的頻道名稱正是「57東森財經新聞」，成立時間標記為2011-11-18，且**當中的影片發布時間戳為2026-07-14（今天）**，證實此頻道確實每天都有新內容更新，**RSS方式可行，已直接驗證非推測**。
3. **內容組成需注意的落差**：實際抓到的RSS最新項目**並非純粹「股市/財經」內容**，而是混合了社會新聞、國際新聞（如「美國驚爆『有活體ET』120CM巨眼？」「名素食店遭車撞後再遇祝融」）與財經內容（去槓桿風暴、川普關稅、通膨等）。**這代表「57東森財經新聞」實質上是東森財經台(頻道57)的完整新聞頻道，不是只播財經新聞的窄頻道**——這點會影響 M2 的YouTube擷取器設計：**必須額外做內容篩選（例如標題關鍵字比對是否為財經相關）**，不能假設該頻道抓到的每支影片都與股市/財經相關，否則會混入大量無關新聞污染最終總整理報告。**此為需要回報給 Planner/使用者的重要發現，非單純技術細節。**
4. **字幕可用性（youtube-transcript-api 能否抓到字幕）**：**本研究無法在不實際執行程式碼的情況下驗證**，因為字幕存在與否、是自動生成或人工上傳，都是每支影片各自獨立的YouTube後端資料，無法透過WebSearch/WebFetch這類唯讀網頁抓取手段確認（YouTube的字幕資料不會顯示在一般HTML頁面或RSS feed中，須透過 `youtube_transcript_api` 或 YouTube Data API 的 captions endpoint 才能查詢）。**What WOULD verify it**：Builder 在 M2 實作時，對當天RSS抓到的最新影片ID，實際呼叫 `YouTubeTranscriptApi.list_transcripts(video_id)` 或 `.get_transcript(video_id, languages=['zh-Hant','zh-TW','zh'])`，並準備好「無字幕則標記略過」（Q6已拍板的fallback）。**經驗性提示（非本研究驗證，[Low]信心）**：台灣電視新聞頻道的YouTube影片，若為「已上傳的剪輯新聞片段」通常較常有中文字幕（部分是電視台自己上的CC字幕，部分是YouTube自動語音辨識）；若為「24小時直播/live」錄影檔，通常**沒有字幕或字幕品質很差**，需 Builder 實測後才能確定。
**來源**：直接 WebFetch `https://www.youtube.com/feeds/videos.xml?channel_id=UCuzqko_GKcj9922M1gUo__w`（成功取得即時內容）；WebSearch 交叉確認 `@57ETFN` handle 與頻道描述。
**信心**：頻道ID/handle正確性 [High]（RSS實際回應+頻道名稱吻合，雙重驗證）；內容混雜財經與一般新聞的發現 [High]（直接觀察到的RSS實際內容，非推測）；字幕可用性 [Low]（明確無法遠端驗證，需Builder實測，已寫明what-would-verify）。

## Conflicts & Caveats

1. **PLAN.md 假設「有 RSS 就用 RSS」但四個核准來源中僅 Yahoo奇摩股市確認有RSS**，cnyes/udn/ctee 三者本研究皆未能找到可用官方RSS（見Findings #2）。這與Q2「抓取原則：有RSS用RSS，沒有才用HTML爬蟲」的決策本身不衝突（原則仍成立），但**實際落地時三分之四的來源會落入「用HTML爬蟲」分支**，這會顯著提高 M2 的工作量與維護風險（HTML結構變動時會斷），Planner/Builder應據此調整工時預期，而非誤以為多數來源可用RSS輕鬆解決。
2. **YouTube頻道內容並非純財經**（見Findings #8第3點）——PLAN.md與User Decisions都預設「東森財經新聞頻道」抓到的內容即為財經新聞，但實測RSS顯示該頻道混雜社會/國際新聞。這是**足以影響M2/M3設計的新事實**，見下方Plan Impact。
3. **youtube-transcript-api 的可靠性有時間敏感性**——PoToken等YouTube反爬蟲機制仍在演進中，本研究只能確認「查詢當下(2026-07)套件仍在维护、且技術上YouTube已知會封鎖雲端IP」，無法保證未來持續可用；Builder/使用者應理解這是**外部依賴風險**而非一次性驗證完就永久有效。
4. **PTT抓取的「技術可行」與「是否應該做」是兩件事**——沒有robots.txt不代表PTT歡迎自動化長期抓取；本研究只能確認「技術上可繞過over18」，法律/服務條款上的許可性本研究無法給出結論性答案（PTT無公開明文ToS條款可查證）。此點PLAN.md本身已預期到（要求Researcher確認可行性，若不可行需回報而非靜默跳過），故不算新衝突，但再次強調風險。
5. **經濟日報/工商時報RSS查證方式有其侷限**——本研究使用的WebFetch工具會將部分內容轉換處理，理論上存在「頁面實際回傳的是有效XML但工具呈現層判斷錯誤」的可能性（例如`money.udn.com/rssfeed/lists/1001`）。建議 Builder 在實作前，用瀏覽器或 `curl`/`requests` 直接對候選URL發一次原始請求二次確認，而非完全採信本研究結論就直接放棄RSS路線。

## Plan Impact

1. **M2（資料擷取器）工作量預估需上修**：PLAN.md 原本可能隱含「多數來源有RSS會比較輕鬆」的假設，但實測顯示僅Yahoo確認有RSS，cnyes/udn/ctee三者都需要HTML爬蟲（且尚未確認各自robots.txt規則，需Builder開工前先各自查一次）。建議 M2 的「風險：高」評級維持不變甚至上修，且Sub-tasks表格或Approach章節應明確寫入「cnyes/udn/ctee目前無確認可用RSS，一律走HTML爬蟲」，避免Builder浪費時間找不存在的RSS。
2. **M2 YouTube擷取器需新增「財經內容篩選」步驟**：「57東森財經新聞」頻道RSS混雜社會/國際新聞，不能整支頻道當日最新影片都視為財經內容直接送進摘要流程。建議在 M2 或 M3（規則篩選引擎）新增一條規則：**對YouTube抓到的影片標題做財經關鍵字比對（如：股市、台股、大盤、個股名稱、財經、投資、升息、降息、通膨、匯率等），不符合者視為非財經內容、當日略過該YouTube來源**，這是PLAN.md目前沒有明確寫到的新規則，建議補進 rules.md。此為**建議變更，非阻塞項**，因為Q6/Q9決策架構本身已容許在rules.md加規則，只是這條規則的必要性是研究後才發現的新資訊。
3. **M8（排程）維持PLAN.md現有判斷「v1不做，延後」**：本研究確認了Task Scheduler+venv的具體做法（見Findings #5），可直接寫入未來M8實作時的Approach章節，但因Q5未拍板且v1 stop condition已排除自動排程，此為「先備而不用」，PLAN.md本身不需要現在修改，只是Researcher提供了做法供未來參考。
4. **M5（分組模組）的資料源已確認可用，無需修改PLAN.md**：TWSE/TPEx CSV端點已驗證可直接下載，PLAN.md中「需 Researcher 確認是否有公開的上市櫃代碼對照資料源」的風險項可視為已解除，Builder可直接採用，無需再找替代方案或退回「不分組」的backtrack。
5. **Unknowns #7（jieba vs CKIP）維持v2選配，不影響v1**：本研究對Windows安裝難易度僅能給出低信心的一般性推論，建議PLAN.md在M6方案A（TextRank，v2選配）的Approach備註中加一句「導入前Builder需自行實測CKIP Tagger在目標Windows機器的安裝流程，勿直接假設順利」，屬於低優先度的文件補充，不影響v1範圍。
6. **其餘（Q1-Q10已拍板項目）**：本研究未發現任何足以推翻使用者已拍板決策的新事實；上述第1、2點是「執行細節上需要調整」而非「決策本身錯誤」，其餘Unknowns（Task Scheduler、TWSE/TPEx、jieba/CKIP）均為支援性資訊，不影響已拍板的Q1-Q10方向。
