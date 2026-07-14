# BUILD LOG

## Deliverables

- `Stocks_Auto/dedup.py` — M4 去重模組（`difflib.SequenceMatcher` 標題相似度，門檻 `config.DEDUP_THRESHOLD`）
- `Stocks_Auto/grouping.py` — M5 分組模組（TWSE/TPEx CSV 公司對照表，快取於 `Stocks_Auto/cache/company_map.json`）
- `Stocks_Auto/summarize.py` — M6 摘要模組（方案B 標題+首段 + 方案C TF-IDF關鍵字標籤，呼叫 `12_Martix_DataSheet.py`）
- `Stocks_Auto/output.py` — M7 輸出模組（JSON，寫入 `config.OUTPUT_DIR`）
- `Stocks_Auto/03_Pipeline.py` — 端到端管線入口點（新建，接續 01/02/12 的編號慣例）
- `Stocks_Auto/fetch_common.py` — 各 HTML 擷取器共用工具（GET 請求、`<p>` 內文擷取）
- `Stocks_Auto/fetch_cnyes.py` — 鉅亨網擷取器（HTML，regex 解析）
- `Stocks_Auto/fetch_udn.py` — 經濟日報擷取器（HTML，JSON-LD 解析）
- `Stocks_Auto/fetch_ctee.py` — 工商時報擷取器（HTML，JSON-LD `@graph` 解析）
- `Stocks_Auto/fetch_ptt.py` — PTT Stock板擷取器（HTML + over18 cookie）
- `Stocks_Auto/fetch_youtube.py` — YouTube 擷取器（RSS + 財經關鍵字篩選 + 字幕嘗試；見 Known Limitations）
- `Stocks_Auto/01_Data_Search.py` — 加註 SUPERSEDED 說明後保留（原始草稿，不再被管線呼叫）
- `Stocks_Auto/websites/Stocks/backend/data/2026-07-14.json` — 實際執行產出的真實資料檔（50篇文章、32個分組，非測試假資料）
- 已刪除：`scratch_article.html`、`scratch_rss_sample.xml`、`scratch_tfidf_out.txt`、`scratch_yahoo_out.txt`、`scratch_yahoo_out2.txt`（除錯用暫存檔，已從中萃取所需資訊後清除）

## Per Sub-task

**M4 去重模組**：完成。`dedup.py` 以 `SequenceMatcher` 比對標題相似度，門檻讀 `config.DEDUP_THRESHOLD`（0.8）；同群代表選取 body 最長者（代理「報導最完整」），其餘列入 `additional_sources`。單元測試（`__main__` 內建樣本）與管線實跑皆確認合併行為正確：52篇篩選後 → 去重為50篇（合併2篇重複）。

**M5 分組模組**：完成。`grouping.py` 下載並快取 TWSE (`t187ap03_L.csv`) + TPEx (`t187ap03_O.csv`) 公司代號對照表（實際下載成功，共 **1980 筆**公司資料），依公司簡稱/名稱長度優先比對 title+body。快取寫入 `cache/company_map.json`，7天內重跑不重新下載（已驗證第二次執行讀快取，未重新發出 HTTP 請求）。實跑結果：50篇分為32組，未分類（大盤/未分類）9篇 = **18%**，低於 PLAN.md 訂定的 <30% 可接受門檻。

**M6 摘要模組**：完成。`summarize.py` 單篇摘要優先用來源 `description`（Yahoo RSS 原生提供，其餘來源以 body 前150字代理），截到 SUMMARY_MAX_LEN=150 字（方案B）；分組關鍵字用 `12_Martix_DataSheet.py` 的 `build_matrix`/`top_keywords` 對組內合併文本取前5高權重詞（方案C）。人工檢視實跑輸出（見下方JSON抽樣）：摘要可讀、關鍵字與內容相關（例：「2330 台積電」組關鍵字含「etf」「市場」，內容確為ETF/台股相關新聞）。

**M7 輸出模組**：完成。`output.py` 組出含 `date`/`generated_at`/`groups[].{group,keywords,article_count,articles[]}` 結構的 JSON，`article` 序列化時將 `pubdate` 轉 ISO字串、移除大型 `body` 欄位只留 `summary`（避免輸出檔過度肥大）。分組排序：文章數多者優先，未分類固定排最後。已用 `json.load` 驗證輸出檔可正常解析、欄位完整。

**入口點 03_Pipeline.py**：完成。串接 6 個來源擷取器 → `rules.apply_rules` → `dedup.dedup` → `grouping.group` → `summarize.summarize_groups` → `output.build_report`/`write_report`。**已實際執行**（非僅寫完未跑），完整 log：
```
=== Stocks_Auto pipeline 開始執行 2026-07-14 ===
[pipeline] yahoo: 擷取 50 篇
[pipeline] cnyes: 擷取 8 篇
[pipeline] udn: 擷取 10 篇
[pipeline] ctee: 擷取 5 篇
[pipeline] ptt: 擷取 14 篇
[pipeline] youtube: 擷取 0 篇（詳見 Known Limitations）
[pipeline] 共擷取 87 篇（去重/篩選前）
[pipeline] rules.md 篩選後剩 52 篇
[pipeline] 去重後剩 50 篇
[pipeline] 分為 32 組
[pipeline] 已輸出：...\websites\Stocks\backend\data\2026-07-14.json
=== 完成，共 50 篇、32 組 ===
```
確認 `websites/Stocks/backend/data/2026-07-14.json` 實際存在於磁碟且為當日真實抓取資料（非樣本/假資料）。

**其他來源（cnyes/udn/ctee/ptt）**：全部完成並驗證可用（見上）。修正過程中發現 `fetch_ctee.py` 首版有 bug（未處理 `<script>` 內容為 JSON 陣列而非單一物件的情況，導致解析不到列表），已修正並重新驗證成功抓到5篇。

**YouTube 來源**：RSS抓取與財經關鍵字篩選（rules.md規則03）皆正常運作（15支影片中10支被篩掉、5支通過關鍵字比對），但實際字幕抓取全數失敗，見 Known Limitations。依 Q6 拍板的 fallback，管線不中斷，該來源當日回傳空清單。

**舊檔清理（Q8）**：`10_LangChain.py`、`11_LamaIndex.py` 確認在磁碟上已不存在（`ls` 驗證），且整個 `Stocks_Auto/` 目錄從未被 git 追蹤過（`git status` 顯示為 `?? ./`），故無需 `git rm`，無歷史可回溯，此為單純確認性紀錄。`12_Martix_DataSheet.py` 維持前一任 Builder 已完成的 TF-IDF term-document matrix 實作，本次直接複用（`summarize.py` 透過 `importlib.import_module("12_Martix_DataSheet")` 呼叫，因檔名以數字開頭無法用一般 `import` 語法）。

**01_Data_Search.py 處理**：未刪除，改為在檔頭加註「[SUPERSEDED / 僅供參考]」說明區塊，明確指出寫死路徑/單一YouTube影片ID等內容已被 `03_Pipeline.py` + `config.py` 取代，且此檔不再被管線呼叫，避免遺留誤導性的「看起來像是活的程式碼」。

**LLM API 依賴掃描（第8項要求）**：`grep -riE "openai|anthropic|generativeai|gpt|api_key"` 對 `Stocks_Auto/` 下所有 `.py` 檔案執行，**零命中**。零 LLM API 依賴的硬性限制已滿足。

## Divergences from Plan

1. **其他來源擷取器命名未依編號慣例**：PLAN/交接指示對「其他來源」未強制要求編號檔名，僅入口點需要；故 `fetch_cnyes.py`/`fetch_udn.py`/`fetch_ctee.py`/`fetch_ptt.py`/`fetch_youtube.py` 採一般模組命名（比照 `rules.py`/`dedup.py`），與 `02_Fetch_Yahoo.py`（已存在、未改動）並存。判斷理由：這些是被 `03_Pipeline.py` import 的函式庫模組而非獨立可執行入口點，比照 `rules.py` 的命名慣例更一致。
2. **未針對 cnyes/udn/ctee 逐一檢查 robots.txt**：RESEARCH.md Conflicts第1點建議「Builder開工前先查一次各站robots.txt」，本次因時間考量未逐一查驗，改以「實際請求成功且無明顯反爬蟲阻擋（無429/403）」作為替代驗證方式。三個來源實測皆為200 OK且能穩定解析，暫判定可用；若未來被封鎖需重新評估。此為風險留存，非隱瞞遺漏，於此明確記錄。
3. **body擷取採用通用 `<p>` 標籤合併法而非各站專屬CSS選擇器**：測試 cnyes 專屬 class（如 `mfxje1x`）後發現其為CSS-in-JS動態產生的class名稱，不穩定；改用「收集所有 `<p>` 標籤文字、濾除過短與樣板關鍵字」的通用方法，更抗網站改版，但代價是內文可能混入少量頁首/側欄短句（已用長度門檻與樣板關鍵字過濾大部分雜訊）。

其餘與 PLAN.md/RESEARCH.md 一致，無其他重大分歧。

## Known Limitations

1. **YouTube 字幕來源實測 0/15 成功**：對「57東森財經新聞」頻道 2026-07-14 當日最新15支影片逐一呼叫 `YouTubeTranscriptApi.list()`，結果：10支被財經關鍵字規則篩掉（非財經內容，符合預期設計）、其餘5支財經相關影片中，**5支全數回傳 `TranscriptsDisabled` 或 `VideoUnplayable`**，即該頻道目前未提供任何字幕（無論自動生成或人工上傳）。這與 RESEARCH.md 已預告的風險吻合（PoToken/反爬蟲機制演進中，字幕可用性需逐日驗證）。管線行為：依 Q6 拍板 fallback，`fetch_youtube.py` 對無字幕影片標記略過、不拋例外，該來源當日回傳空清單，`03_Pipeline.py` 正常繼續執行其餘來源，**未中斷整體流程**（已於實跑log中確認）。此為每日皆可能發生的常態限制，非一次性bug，若使用者需要此來源真正產出內容，需另外評估語音辨識（會違反零LLM限制，需使用者重新拍板）或改抓其他有字幕的頻道/來源。
2. **cnyes/udn/ctee robots.txt 未逐一查驗**（見Divergences第2點），屬已知風險保留項，未阻塞v1交付。
3. **cnyes/udn/ctee/ptt 皆為HTML結構依賴的爬蟲，非官方RSS**：任何一個網站的前端改版（class名稱、JSON-LD結構變更）都可能讓對應擷取器失效。`fetch_ctee.py` 已在本次開發過程中遇到一次典型案例（JSON-LD內容為陣列而非物件導致解析失敗），已修正，但無法保證未來不會再發生同類問題；每個擷取器失敗時僅印出訊息並回傳空清單，不會讓 `03_Pipeline.py` 崩潰，此為設計上的容錯而非「保證永久可用」。
4. **PTT 抓取屬灰色地帶**：無官方 robots.txt、無明文 ToS 允許自動化定期抓取，僅技術上可行（over18 cookie 為業界成熟做法）。使用者於 PLAN.md Q2 已知悉此風險並核准納入。若之後 PTT 端出現速率限制/封鎖，`fetch_ptt.py` 會回傳空清單並印出失敗訊息，不影響其他來源。
5. **公司分組為子字串比對，非語意消歧**：`grouping.py` 用公司簡稱/名稱字串直接比對 title+body，可能有少量誤判（例如新聞中提及公司名稱但主體其實是不相關話題）。實跑結果未分類比例18%（在<30%可接受範圍內），但未逐篇人工複核全部32組的分類正確性是否100%精準，僅抽樣檢視前5組結果看起來合理。
6. **摘要品質未做大規模人工評測**：僅對實跑輸出的前幾組做抽樣檢視（見Per Sub-task M6），確認摘要可讀、關鍵字相關，未對全部50篇逐一覆核。
7. **`01_Data_Search.py` 保留但已加註棄用說明，非物理刪除**：與 Q8 決策（僅刪除10/11、12重新定義）不完全對應，因為 01 檔案本身在 Q8 的選項中並未被明確要求「刪除」，交接指示第7點也只要求「決定要不要留、若superseded要說明」而非強制刪除，故採取「加註說明保留」而非刪除，理由：保留原始需求的歷史脈絡，且刪除屬破壞性操作，指示未明確授權對這個檔案做刪除。

## Revision Round 1 (response to REVIEW.md)

REVIEW.md 判定 REVISE，列出 1 個 BLOCKER + 2 個 MAJOR（另有 2 個 MINOR 明確要求本輪不處理）。以下是針對這 3 項的修復與驗證紀錄。所有驗證皆為本輪重新實際執行（非僅閱讀程式碼推論），細節與原始輸出檔已在下方逐項列出。

### Fixes Applied

**BLOCKER — grouping.py 子字串誤判（分三層修法，均在 `Stocks_Auto/grouping.py`）**

REVIEW.md 抽查的 7 個假陽性案例背後其實是三種不同的根因，逐一對應修法：

1. **短簡稱需要更強訊號**（新增 `_has_valid_match()`，取代原本單純的 `keyword in text`）：長度 <= `SHORT_KEYWORD_MAX_LEN`(=3) 的簡稱，不再是「body 內任一子字串命中即算數」，改為要求「標題命中」或「股票代號數字出現在該次命中前後 `CODE_PROXIMITY_WINDOW`(=20) 字元窗口內」（`_code_near()`）。對應修復：世界(WHO)、新建(新建案)、大台北(換屋族)、中華(貿協)、大田(陳大田人名) 5個案例。長度 > 3 的名稱（台積電、台塑、華新科等）維持原行為，不犧牲回收率。
2. **排除性列舉子句偵測**（`_is_exclusion_clause_occurrence()`）：即使是長公司全名（如「三商投資控股股份有限公司」11字，不受規則1影響），若其命中位置前方鄰近出現「不含/不包括/不計入/扣除」、且後方鄰近出現「計X家/共X家」彙總計數語，視為統計揭露文字裡的「不算在內」清單成員、非報導主體，判定為無效命中。對應修復：REVIEW.md 的 2905 三商案例（原本的「三商」誤判實際上是全名「三商投資控股股份有限公司」命中「不含金融保險業32家及三商投資控股股份有限公司計33家」這句排除子句，並非簡稱本身的問題，比 REVIEW.md 原始歸因更精確）。
3. **常用詞/地名碰撞清單**（`COMMON_WORD_COLLISION_KEYWORDS`）：驗證修法時用實際 2026-07-14 即時資料重跑 pipeline 並逐一稽核**每一個** `article_count:1` 的分組（見下方 Verification），額外發現規則1的「標題命中即有效」對「官方簡稱本身就是通用詞彙/地名」的公司仍不夠嚴謹——例如代號5347世界先進的官方簡稱直接是「世界」兩字、代號1473台南企業的官方簡稱直接是「台南」兩字、代號5007三星科技的官方簡稱「三星」正好與南韓Samsung同名、代號4923的官方簡稱「力士」正好是「海力士(SK Hynix)」的子字串。對這份清單內的關鍵字，即使命中在標題裡也不直接放行，仍套用規則1的代號鄰近共現檢查。清單分兩類：(a) 台灣22縣市/地區行政區名稱（封閉、可窮舉的集合，一次性收錄降低此類地名碰撞風險）；(b) 個別驗證到的「簡稱=通用詞彙/知名品牌」案例（世界、新建、中華、大田、三星、力士）。此類 (b) 明確**不是**窮舉，已在 Remaining Known Limitations 誠實記錄。

**MAJOR — summarize.py 靜默截斷（修復點在 `fetch_cnyes.py`／`fetch_ctee.py`／`fetch_ptt.py`／`fetch_youtube.py`／`fetch_udn.py`，`summarize.py` 本體邏輯未變）**

把 5 個 fetch_*.py 裡原本 `"description": body[:150]`（或 `transcript[:150]`）的預先截斷全部改成傳遞完整 `body`／`transcript`：
- `fetch_cnyes.py`、`fetch_ctee.py`、`fetch_ptt.py`、`fetch_youtube.py`：`description` 直接等於完整 body/transcript。
- `fetch_udn.py`：原本邏輯是「原生 description 優先，空的話 fallback 到 `body[:150]`」，fallback 也同樣有這個 bug，改為 fallback 到完整 `body`。
`summarize.summarize_article()` 本身的 `if len(text) > SUMMARY_MAX_LEN: 截斷+"…"` 邏輯完全不用改，只要輸入不再被預先剪到剛好150字，這個既有判斷就會正確觸發。

**MAJOR — dedup.py 純標題相似度誤合併（修復點在 `Stocks_Auto/dedup.py`）**

新增 `_should_merge()`（取代原本 `dedup()` 迴圈裡直接呼叫的 `_title_similarity(...) >= threshold` 判斷），標題相似度達門檻後還需通過兩關才真正合併：
1. `_distinguishing_conflict()`：`DISTINGUISHING_TERM_GROUPS = [{"外資", "投信", "自營商"}]` 區辨詞規則，若兩標題分別命中同一組裡的不同詞，直接否決合併。
2. `_body_similarity()`：body 內容字元 bigram（2-gram）Jaccard 相似度需達到 `BODY_SIMILARITY_MIN`(=0.15，刻意寬鬆) 才放行；任一方沒有 body 可比對時保守地不當作否決訊號（回傳1.0，避免因某來源擷取失敗而誤擋正常合併）。

### Verification

**BLOCKER 分組修法驗證（含 REVIEW.md 要求的「稽核每一個 article_count:1 分組」）**

1. **REVIEW.md 原始 7 個假陽性案例回歸測試**：用與 `cache/company_map.json` 實際資料結構一致的公司資料，重建 REVIEW.md 描述的 7 個情境（世界/WHO、新建/新建案、大台北/換屋族、中華/貿協、大田/陳大田人名、中石化/側欄污染情境、三商/排除性統計子句），全部 7/7 修法後正確落入「大盤/未分類」（PASS），而 4 個真陽性對照組（台積電標題命中、台塑標題命中、三商真正法說會報導、世界先進代號鄰近共現）全部 4/4 正確維持分類（PASS）。
2. **實際重跑 `03_Pipeline.py` 產出全新 2026-07-14.json，並稽核「每一個」`article_count:1` 分組（非抽樣前5組）**：本輪共重跑 pipeline 5 次（每次因即時網路資料變動、PTT一度連線中斷等因素，抓到的文章組合略有不同），每次跑完都用一支臨時稽核腳本（`_audit_groups.py`，驗證後已刪除）把分組流程重跑一次並印出「每個單篇分組的比對關鍵字＋命中前後文字窗口」，逐條人工判讀是否為真陽性。過程中額外發現並修復了 3 個 REVIEW.md 未提及、但同一根因類型的假陽性（2905三商的長名稱排除子句版本、5347世界先進標題內嵌於「全世界」、1473台南企業標題內嵌於地名列舉、5007三星科技與南韓Samsung同名、4923力士與「海力士(SK Hynix)」子字串），逐一修法後最終一輪的完整稽核結果：
   - 最終一輪重跑：`共擷取 90 篇（去重/篩選前） → rules.md 篩選後 56 篇 → 去重後 53 篇 → 分為 20 組`，其中 `article_count:1` 的分組共 15 組，**15/15 人工核實為真陽性**（逐條列出於稽核紀錄，例如「2330 台積電」標題命中、「4530 宏易」公司自身更名公告內文命中且代號4530確實在同一篇文章別處出現、「2910 統領」「5880 合庫金」皆為公司自身 MOPS 重大訊息公告、「6415 矽力*-KY」「2449 京元電子」皆為 PTT 買賣超排行表格內代號緊鄰簡稱的真實共現）。
   - 未分類（大盤/未分類）比例：`26/53 ≈ 49%`（本輪含較多與個股無關的總經/國際新聞與179篇不構成單一公司分組的內容，比例上升主要來自本次額外驗證跑的資料組成差異，非分組邏輯劣化——若與 BUILD_LOG.md 原始 18% 比較沒有直接可比性，因為兩次抓到的文章池不同；本輪的重點驗證指標是「已分類的單篇組是否為真陽性」而非未分類比例本身，此點依 REVIEW.md 建議#4 已改為稽核方法本身）。
3. **Before/after 具體對照**（同一篇「你待的公司生意爆表？證交所：6月0產業營收衰退」文章）：
   - **修法前**（原始 BLOCKER 描述）：落入「2905 三商」分組，比對命中「三商投資控股股份有限公司計33家」這句排除性列舉文字。
   - **修法後**：`_is_exclusion_clause_occurrence()` 判定該命中位置前方25字內有「不含」、後方25字內有符合 `[計共]\d+家` 的「計33家」，視為無效命中，該篇正確落入「大盤/未分類」。
4. **Before/after 具體對照**（cnyes「全世界陪韓股去槓桿...」文章，實際重跑時發現的新案例）：
   - **修法前**（若只套用 REVIEW.md 原始建議的規則1+2）：仍會落入「5347 世界」分組（因為「世界」出現在標題「全世界」裡，規則1的「標題命中即有效」會誤放行）。
   - **修法後**：因「世界」被列入 `COMMON_WORD_COLLISION_KEYWORDS`，即使命中在標題也需代號鄰近共現，該文章全文找不到「5347」，正確落入「大盤/未分類」。

**MAJOR summarize.py 截斷修法驗證**

1. 直接讀取本輪重跑後的 `websites/Stocks/backend/data/2026-07-14.json`，對**全部**非Yahoo來源（cnyes/ctee/ptt）文章的 `summary` 欄位逐一檢查：**全部** summary 長度 >150 字時皆正確以「…」結尾（無一例外，含大盤/未分類組內的非Yahoo文章）。
2. REVIEW.md 明確點名的 3 個案例（1402遠東新、3481群創、2449京元電子）：因為資料是即時抓取，1402遠東新、3481群創這兩篇原始文章在本輪重跑時已不在當日列表裡（PTT/cnyes當日文章隨時間流動），無法用同一篇文章直接複驗；但 **2449京元電子** 這個案例本輪仍存在（PTT「[情報] 0714 上市外資買賣超排行」），已直接確認其 summary 正確以「…」結尾（修法前是硬斷在數字中間、無省略號，即 REVIEW.md 描述的「261」處硬斷）。另外用單元層級測試（模擬「fetch端傳入超過150字的完整body」情境）直接驗證 `summarize.summarize_article()` 的截斷+省略號邏輯本身正確觸發，len=151、以「…」結尾，證明修法對任何超長 description 輸入都成立，不依賴當天剛好抓到哪幾篇文章。

**MAJOR dedup.py 誤合併修法驗證**

1. `dedup.py` 內建 `__main__` 迴歸測試（`.venv/Scripts/python.exe dedup.py`，已執行且全部 assert 通過，無 traceback）：
   - 樣本1（基本案例）：3篇輸入（2篇同事件不同措辞標題+1篇無關新聞）→ 去重後2篇，正確合併。
   - 樣本2（REVIEW.md 負面案例回歸測試）：「[情報] 0714 上市投信買賣超排行」vs「[情報] 0714 上市外資買賣超排行」，標題相似度計算為 **0.8947**（與 REVIEW.md 獨立算出的數字一致，>= 0.8門檻），去重後仍為**2篇**（不合併）——區辨詞規則正確攔截。
   - 樣本3（正面控制組）：兩篇標題近乎相同、body高度重疊（同事件不同來源）的京元電子模擬案例 → 去重後**1篇**（成功合併），證明修法沒有把 dedup 整個關掉。
2. **實際重跑 `03_Pipeline.py` 產出的真實輸出檔驗證**：
   - 「[情報] 0714 上市投信買賣超排行」（矽力*-KY所在分組）與「[情報] 0714 上市外資買賣超排行」（京元電子所在分組）在最終輸出裡是**兩個獨立分組**，未被合併，`additional_sources` 皆為空，確認 REVIEW.md 的具體案例在真實資料上不再誤合併。
   - 同時在真實輸出中找到 2 組**正面控制案例**（非人工構造，是本輪重跑時真實發生的合併）：「鴻海首次前進2026日本臺灣形象展...」與「無懼股災！「第四法人」逆勢加碼 0050、00631L成交再破百億」兩篇，皆為 Yahoo 與 cnyes 標題**逐字完全相同**（顯然是轉載/聯合供稿），去重後正確合併、對方列入 `additional_sources`，證明修法後「真正的重複」仍正常運作。

**整體管線重新執行確認**：本輪多次以 `.venv\Scripts\python.exe 03_Pipeline.py` 實跑（非僅讀程式碼），最終一輪 exit code 0，`共擷取 90 篇（去重/篩選前） → rules.md 篩選後 56 篇 → 去重後 53 篇 → 分為 20 組`，輸出檔案 `websites/Stocks/backend/data/2026-07-14.json` 可正常 `json.load` 解析、欄位完整（沿用原有 schema，未新增/變更任何輸出欄位）。

### Remaining Known Limitations

1. **`COMMON_WORD_COLLISION_KEYWORDS` 的「簡稱=通用詞彙/知名品牌」清單（`_KNOWN_COMMON_WORD_SHORT_NAMES`）本質上無法窮舉**：本輪修法過程中，每重跑一次就至少多發現一個新案例（世界→台南→三星→力士），這證明「短公司簡稱剛好等於常用詞/知名品牌」是一個長尾問題，不是一次性能列舉完的封閉集合（相對地，台灣縣市地名清單`_TAIWAN_PLACE_NAMES`是封閉集合，這部分較無疑慮）。誠實陳述：本輪已修復所有**本次稽核實際發現**的案例（共6個：世界/新建/中華/大田/三星/力士），並通過了 REVIEW.md 原始 7 個案例的完整回歸測試，但未來換一批新聞資料時，理論上仍可能出現本清單未涵蓋的新收藏字/品牌名巧合。長期更根本的解法會需要語意層級的消歧（例如判斷文章主要語境是否為台灣股市），但這已超出「不用LLM/避免額外NLP依賴」的v1範圍，故本輪僅採用清單+訊號式的務實修法，未來若持續發現新案例，建議直接擴充 `_KNOWN_COMMON_WORD_SHORT_NAMES`。
2. **`_code_near()`／代號鄰近共現的視窗（20字）是經驗值，非理論最佳值**：對「代號和簡稱隔得比較遠」的排版（例如某些法人買賣超表格欄位對齊方式不同）可能仍會漏接（變成分類過嚴、掉進未分類），這是「寧可少分類、不要分類錯」的刻意取捨，符合 REVIEW.md BLOCKER 對精確度優先於召回率的關切方向，但因此本輪未特別驗證「是否因此增加了大盤/未分類的比例、犧牲了多少原本正確的召回」——本輪 49% 未分類比例含有這個效應，但因為抓取的文章池本身逐輪不同，無法乾淨地拆解出「因本次修法而新增的未分類量」與「純粹因為當天新聞內容本來就偏總經、非個股新聞」兩者的占比，這點誠實記錄為未完全量化的取捨。
3. **`fetch_common.py` 的側欄排除（`_is_in_sidebar_container`）只對走 `extract_body_from_paragraphs()` 的來源生效**（cnyes/udn/ctee），PTT 走的是不同的擷取路徑（`fetch_ptt.py` 直接對 `#main-content` 用 `get_text()`），不受此次側欄修法影響；但PTT本身版面結構不同，不太會有「延伸閱讀側欄」這類污染源，故評估風險較低、未特別處理。
4. **dedup.py 的 `BODY_SIMILARITY_MIN=0.15` 門檻是刻意寬鬆值，未做大規模參數掃描**：只用本輪能取得的正面/負面案例驗證方向正確（負面案例被擋、正面案例仍合併），未對大量歷史資料做系統性的門檻敏感度分析；若未來實際使用中發現仍有「內容差異大但字元bigram剛好重疊超過0.15」的邊界案例被誤合併，或反過來「真正重複但body差異略大於0.15被誤擋」的案例，門檻值本身可能需要再微調，這是可預期需要迭代的部分，非一次性解決。
5. **未觸碰的既知 MINOR 項目**（依交接指示明確排除，非本輪遺漏）：dedup.py 的 cluster[0]-only 比對（非 complete-linkage）與 cnyes/udn/ctee robots.txt 未逐一查驗，均維持 REVIEW.md 判定的「不阻塞、可留待未來」狀態，本輪未做任何修改。
