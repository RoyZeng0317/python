# REVIEW

## Verdict: REVISE

## Success Criteria Check (criterion -> met / not met, evidence)

1. **有清楚、使用者已拍板的規劃文件 (PLAN.md/RESEARCH.md)** -> **Met**. PLAN.md 的 Q1-Q10 全部在「User Decisions (Resolved)」有明確拍板；RESEARCH.md 對每項 Unknown 都給出信心標記與來源，並在「Plan Impact」誠實列出對 M2/M2-YouTube 的修正建議。[High, 直接讀取兩份文件確認]

2. **最終腳本能夠：擷取 -> rules.md篩選 -> 去重 -> 分組 -> 非LLM總整理 -> 輸出JSON 到 repo 內正確路徑** -> **部分不符 (Not fully met)**。管線本身確實端到端可跑（見下方「獨立交叉檢查」，我實際執行了一次，exit code 0），六個來源、rules 篩選、輸出檔案位置 (`websites/Stocks/backend/data/2026-07-14.json`) 都正確。但「去重」與「分組」與「總整理」三個步驟在**正確性**上有具體、可重現的缺陷（見下方 Issues #1-#3），不是「有沒有跑」的問題，而是「跑出來的結果是不是它宣稱的東西」的問題。BUILD_LOG.md 對這三個模組的驗證方式（計數比對、抽樣前5組、`json.load`可解析）都通過，但這些驗證方法本身不足以偵測我發現的問題類型，屬於驗證方法的盲點。

3. **全程零LLM API依賴** -> **Met，已獨立驗證**。見下方「獨立交叉檢查」第1項，非僅採信 BUILD_LOG.md 的宣稱。

4. **使用者能手動執行一次，全流程不崩潰、產出檔案格式符合預期** -> **Met，已獨立驗證**。見下方「獨立交叉檢查」第2項，我實際執行了 `03_Pipeline.py`。

## Issues (severity, description, suggested fix)

### BLOCKER — 分組模組 (grouping.py) 對「短公司簡稱」的子字串比對誤判率極高，導致「依公司分組」這項核心功能實質上不可信

PLAN.md Q3 明確拍板「依股票/公司分組」為報告呈現方式的核心決策，也是使用者要的「總整理」的主要價值所在。我對輸出的 `2026-07-14.json` 中 7 個非顯而易見的分組做了獨立抽查（直接重新 fetch 該篇文章原始 HTML、抽出 body、搜尋比對用的公司關鍵字），結果 **6/7 是明確的假陽性**：

- `"5347 世界"` 組收錄一篇健保30年報導，比對命中的是「世界衛生組織（WHO）」裡的「世界」，與世界先進(5347)完全無關。
- `"2516 新建"` 組收錄一篇房市報告，命中的是「新建案完工」的「新建」（一般中文詞），與股票代號2516公司無關。
- `"9908 大台北"` 組收錄一篇房地合一稅報導，命中的是「大台北資產換屋族」的「大台北」（地理區域名稱），與大台北瓦斯(9908)無關。
- `"2204 中華"` 組收錄一篇台中會展中心報導，命中的是「中華民國對外貿易發展協會」裡的「中華」。
- `"8924 大田"` 組收錄一篇交通改善新聞，命中的是「台中市建設局長**陳大田**」——比對命中的是官員的個人名字，不是公司。
- `"1314 中石化"` 組命中的「中石化」字串，來自頁面內嵌的其他文章連結/側欄推薦文字（fetch_common.py 用「收集所有 `<p>` 標籤」的通用擷取法會把頁面上不相關的「延伸閱讀」類文字一併併入 body），該文章本身與中石化(1314)無關。
- `"2905 三商"` 組命中的是統計附註裡「不含金融保險業32家及三商投資控股股份有限公司計33家」這句排除性文字，非真正報導三商集團的新聞。

BUILD_LOG.md 用「未分類比例18% < 30%可接受門檻」＋「抽樣檢視前5組看起來合理」作為驗證方法，但這個指標只衡量「有沒有命中」，不衡量「命中得對不對」；抽樣的前5組恰好是文章數較多、公司名稱本身就出現在標題裡的組（如「2330 台積電」「1301 台塑」「2492 華新科」），沒有覆蓋到我上面查到的這些單篇假陽性組。32組中有22組是 `article_count: 1` 的單篇組，這類組正是最容易受此問題影響的族群。

**Root cause**：`grouping.py` 的 `_build_lookup()` 只過濾 `len(keyword) < 2` 的極短詞，沒有排除常用中文詞彙（世界、新建、大田…恰好也是公司簡稱的常見詞）、沒有姓名消歧、也沒有對抗 `fetch_common.py` 通用擷取法帶入的側欄雜訊。

**建議修法**（任一或組合）：
1. 建立公司簡稱的停用詞表，排除與常用詞、地名、姓氏組合重疊的簡稱，或要求簡稱命中時做人工複核清單。
2. 提高比對信心：要求關鍵字命中發生在標題內，或命中次數/位置有更強訊號（例如同時出現股票代號數字），而非任意出現在整段 body 中一次即算數。
3. 修正 `fetch_common.extract_body_from_paragraphs`，加強排除「延伸閱讀/相關新聞」區塊的 `<p>`（可用 DOM 結構如特定容器 class，而非只靠關鍵字黑名單），避免無關側欄文字污染比對來源。
4. 驗證方法本身要改進：不能只看「未分類比例」，需要對「已分類」的組再做一次「命中理由是否合理」的抽查（至少覆蓋所有 `article_count: 1` 的單篇組），而不是只抽前5組。

### MAJOR — 摘要 (summarize.py) 對非Yahoo來源存在「靜默截斷、無省略號」的重複截斷 bug，導致多數非Yahoo文章摘要看起來完整實則斷在句子中間

`fetch_cnyes.py`/`fetch_ctee.py`/`fetch_ptt.py`/`fetch_youtube.py` 在擷取端就先把 `description` 欄位設成 `body[:150]`（剛好等於 `summarize.SUMMARY_MAX_LEN`）。`summarize.summarize_article()` 的邏輯是 `if len(text) > SUMMARY_MAX_LEN: 截斷+加"…"`，但因為 `description` 長度已經精確等於150（不大於150），這個條件恆為 False，所以省略號永遠不會被加上——文章看起來像是自然結束，但其實是句子中間硬生生被切斷。

**已在實際輸出的 `2026-07-14.json` 中直接觀察到多個案例**（無需重新抓取即可驗證，我是直接讀輸出檔案發現的）：
- `"1402 遠東新"` 組摘要結尾：「...力麗(1444)加工絲產線的產能利用率約維持在8成、集盛(1455)專注高值化產品產能利用率的提升。\n遠東新的聚酯與化纖本業產能」——句子硬生生斷在「產能」兩字，無省略號。
- `"3481 群創"` 組（PTT來源）摘要結尾：「...股本比群創小很多\n:\n: 我是不知道10/20/30不買群創」——同樣硬斷，無省略號。
- `"2449 京元電子"` 組（PTT來源）摘要結尾：「...證券代號　　　　證券名稱　　　　　　　　買超張數\n261」——斷在一個數字中間，無省略號，讀者會誤以為資料有異常或摘要壞掉。

這類問題影響 cnyes(8篇)/ctee(5篇)/ptt(14篇) 共 27 篇（占本次輸出50篇中過半），udn 若原生 description 為空、fallback 到 `body[:150]` 時同樣會中招。BUILD_LOG.md「人工檢視實跑輸出...摘要可讀」的結論與此不符，判斷是抽查樣本沒有覆蓋到非Yahoo來源的截斷邊界案例。

**建議修法**：不要在 `fetch_*.py` 裡預先把 description 截到剛好等於 `SUMMARY_MAX_LEN`；改成傳遞完整（或明顯更長於150）的內容，統一交給 `summarize.py` 判斷是否需要截斷並加省略號；或在 fetch 端截斷時就直接帶上省略號標記供 summarize.py 辨識「這段本來就被截過」。

### MAJOR — 去重模組 (dedup.py) 純標題相似度比對，在真實輸出中已造成兩篇「內容不同但標題相似」的文章被誤判為重複，導致其中一篇內容實質遺失

在輸出的 `"2449 京元電子"` 分組中，`additional_sources` 把 PTT 貼文「[情報] 0714 上市**投信**買賣超排行」標記為「[情報] 0714 上市**外資**買賣超排行」的重複來源。我用專案本身的 `SequenceMatcher` 獨立計算兩個標題的相似度為 **0.8947（≥ 0.8 門檻）**，故被合併——但這兩篇文章報導的是**不同的統計主體**（外資買賣超排行 vs. 投信買賣超排行），內容完全不同，不是同一則新聞被兩個來源轉載。合併後，「投信買賣超排行」這篇的完整內容（body/summary）從輸出中消失，只剩下 `additional_sources` 裡的一個標題+連結存根，讀者若只看 JSON 會誤以為兩篇是重複報導，實際上遺失了一份獨立資訊。

這正是 PLAN.md 自己在 M4 的 Backtrack trigger 裡預先設想的失敗模式（「若誤合併...改用Q7(d)複合判斷」），而且已經在正式輸出裡真實發生，不是理論上的邊界案例。BUILD_LOG.md 對 M4 的驗證只做了計數比對（「52篇→50篇，合併2篇重複」）與內建的3筆樣本測試，樣本測試本身没有涵蓋「標題相似但內容主體不同」這種情境，故未能攔截這個問題。

**建議修法**：在標題相似度之外至少加一個輔助訊號再判定合併，例如：body 內容的 Jaccard/TF-IDF 相似度、或發布時間差、或關鍵數字/代號是否一致（此例中「外資」vs「投信」這種主體詞若被視為不可忽略的差異詞，應該直接否決合併）。PLAN.md Q7(d) 選項本身就是為了這種情況準備的，建議按此補強。

### MINOR — dedup.py 的分群邏輯只比對「新文章 vs. 群組中第一篇」，不是完全連鎖（complete-linkage），對長鏈近似重複可能漏合併

`dedup()` 內部迴圈是 `_title_similarity(article["title"], cluster[0]["title"])`，只跟每個群組的**第一篇**比較，不是跟群組內所有成員或代表比較。我用構造的 A→B→C 三則「逐步加字」的標題鏈測試（A~B=0.71 未達門檻、B~C=0.80 達門檻、A~C=0.54 未達門檻），結果為 A 自成一群、B+C 合併——這是合理結果，不是本次測試暴露出的 bug；但如果換成 A~B、B~C 都達門檻、A~C 卻些微低於門檻的排列，C 仍會因為只跟 cluster[0]=A 比較而可能被錯誤地拆到另一群，即使它與 B（已在群內）高度相似。這屬於已知演算法設計限制，方向是「少合併」而非「錯合併不相關文章」，風險低於上面兩個 MAJOR 項目，故列為 MINOR，不影響 verdict，但建議之後有資料量變大時留意。

### MINOR — cnyes/udn/ctee 的 robots.txt 仍未逐一查驗（BUILD_LOG.md 已自陳此風險，非新發現）

RESEARCH.md Conflicts 已建議查驗，BUILD_LOG.md Divergences #2 已誠實記錄「因時間考量未逐一查驗」並說明替代驗證方式（實測200 OK無明顯反爬蟲阻擋）。這是已知、已揭露的風險，不是隱瞞，維持 MINOR，不阻塞。

## What Was Independently Cross-checked

1. **零LLM依賴**：獨立執行 `grep -riE "openai|anthropic|generativeai|gpt|api_key"` 於 `Stocks_Auto/` 下所有 `.py`，**零命中**，與 BUILD_LOG.md 宣稱一致。另外額外自行擴大檢查，搜尋所有 `requests.post`/`requests.get`/`urlopen`/`httpx.` 呼叫，確認全部目標皆為 Yahoo RSS/文章頁、YouTube RSS feed、TWSE/TPEx CSV — 沒有任何指向 LLM 服務商網域或形似 LLM API 的呼叫（無 `requests.post` 存在於任何檔案）。[High confidence, 獨立指令執行]

2. **管線是否真的能跑**：我實際啟動 `.venv\Scripts\python.exe 03_Pipeline.py` 執行一次完整流程（先備份原始 `2026-07-14.json`，跑完後已還原，未破壞既有交付物）。Exit code 0，六個來源全部正常擷取（yahoo 50、cnyes 8、udn 10、ctee 5、ptt 14），YouTube 15支影片中10支被財經關鍵字篩掉、5支全數 `TranscriptsDisabled` 被優雅跳過（親眼在 log 中看到 `[youtube] ... 無法取得字幕（略過，不中斷流程）：TranscriptsDisabled`，管線繼續正常執行到輸出完成），與 BUILD_LOG.md「不中斷整體流程」的宣稱完全吻合。[High confidence, 直接執行取得]

3. **輸出JSON結構**：`json.load` 成功解析、欄位齊全（`date`/`generated_at`/`group_count`/`total_articles`/`groups[].{group,keywords,article_count,articles}`），中文皆為正確UTF-8（`ensure_ascii=False`），無亂碼。所有文章 `pubdate` 均為 2026-07-14，符合規則02「只取當日新聞」。[High confidence]

4. **rules.md 規則01 (600字)**：重新對7篇文章直接 fetch 原始頁面並用專案自帶的 `extract_body_from_paragraphs` 抽取 body，長度介於736~3793字，遠高於600字門檻。[High confidence，惟這是重新抓取當下的版本，非管線執行當下的快照，但可作為規則邏輯正確性的合理佐證]

5. **rules.md 規則03 (YouTube專屬財經關鍵字篩選)**：讀 `rules.py` 確認 `passes_youtube_financial_filter` 對非youtube來源直接回傳 `True`（不影響其他來源），只對 `source == "youtube"` 的文章做關鍵字比對，範圍正確，與 BUILD_LOG.md 宣稱一致。[High confidence]

6. **01_Data_Search.py 是否為死碼**：獨立執行 `grep -rn "01_Data_Search"` 於所有 `.py` 檔案，除了它自己的檔案內容外沒有任何其他檔案 import 或引用它，確認未被 `03_Pipeline.py` 呼叫。[High confidence]

7. **git 追蹤狀態**：獨立執行 `git status`／`git rev-parse --show-toplevel`，確認 git 根目錄在 `Stocks_Auto` 的上一層，整個 `Stocks_Auto/` 目錄對這個 repo 而言是未追蹤狀態，與 BUILD_LOG.md「無需git rm」的說法一致。[High confidence]

8. **殘留他機路徑**：獨立搜尋 `C:\Users\roy`，僅存在於 `01_Data_Search.py`（已標記SUPERSEDED且確認為死碼）與 `team-run/PLAN.md` 的文件敘述文字中，沒有任何會被執行到的程式碼路徑殘留舊路徑。[High confidence]

9. **分組模組正確性**（超出 BUILD_LOG.md 宣稱範圍的獨立驗證）：對7個非顯而易見的分組結果重新抓取原始文章驗證比對邏輯是否合理，發現6/7為假陽性，詳見上方 BLOCKER 項目。[High confidence，直接抓取原始頁面比對]

10. **去重模組邊界案例**（超出 BUILD_LOG.md 宣稱範圍的獨立驗證）：用專案自帶的 `SequenceMatcher` 重新計算實際輸出中被合併的兩篇PTT文章標題相似度為0.8947，並額外構造「完全相同標題」「門檻邊界值恰為0.8」「三則標題鏈」等測試案例驗證 `dedup.py` 行為，發現真實輸出中已出現一起誤合併案例，詳見上方 MAJOR 項目。[High confidence]
