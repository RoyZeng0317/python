# 需求
目前拆分為網站與手機介面，核心語言為python
希望能夠拆分成十個進度
每個進度為兩小時進行
一共採用20天進行

<!-- 我新增了專注時鐘.py 作為顯示當前時間的部分 -->
註解不可刪除

# 架構
lib 當中有 learning_process.py 作為網站與手機業面的需要 Library(庫)

## 已實作內容

### 檔案結構
- `lib/Learning_Process.py` — 排程／進度／匯出核心邏輯：10 個進度、每個 2 小時、間隔 2 天、共 20 天，4 個科目輪替
- `lib/專注時鐘.py` — 顯示目前時間 + 管理單一進度的專注計時（`FocusClock`）
- `websites/backend/app.py` — FastAPI 後端，統一提供 API 並掛載前端靜態檔（單一 port，網站與手機瀏覽器共用同一個 responsive 介面，不需另外開發原生 App）
- `websites/frontend/` — `index.html` / `style.css` / `script.js`；手機版透過 `@media (max-width: 480px)` 調整
- `data/progress.json` — 進度存檔，首次啟動自動產生

### 啟動方式
```powershell
cd Learning_Path/websites/backend
pip install -r requirements.txt
python app.py
```
瀏覽器開啟 http://localhost:8001 ；手機瀏覽器需與電腦在同一網段，改用電腦的區網 IP 開啟。

### API
- `GET /api/plan` 取得 10 個進度
- `GET /api/progress` 完成度摘要
- `POST /api/stage/{id}/start` 開始該進度的 2 小時專注計時
- `POST /api/stage/{id}/complete` 完成該進度
- `GET /api/export/markdown` 匯出 markdown 報告
- `POST /api/plan/reset` 重新產生 20 天排程
