# 需求
在 `AI_img/` 資料夾內製作「影像捲積 (2D Convolution)」的 Python 範例程式，讀取一張圖片、套用自訂 kernel、並用 matplotlib 顯示原圖與卷積後的對照結果。

# 架構 / 檔案結構
- `影像捲積.py` — 主程式
  - `imread_unicode(path, flags)` — 用 `np.fromfile` + `cv2.imdecode` 讀圖，避開 Windows 上 `cv2.imread` 對中文路徑常失敗的問題
  - `convolve2d(image, kernel)` — 手刻 2D 卷積：zero padding 補邊、輸出尺寸與輸入相同、依 kernel 權重總和正規化避免亮度爆掉
  - `path` — 圖片路徑（目前指向 `蒙娜麗莎.JPG`）
  - `Kenernel` — 3x3 卷積核心（變數名稱維持原拼字，未更動）
  - `if __name__ == "__main__":` — 讀圖 → 轉灰階 → 套用 kernel → matplotlib 左右對照顯示
- `蒙娜麗莎.JPG` — 範例輸入圖片

# 執行動作紀錄

- 2026-07-29：初版建立於專案根目錄 `影像捲積.py`，只有 import + 空 kernel 定義。
- 2026-07-29：補上 `imread_unicode()` 與手刻 `convolve2d()`，接上主程式區塊，讀圖 → 灰階 → 卷積 → matplotlib 雙圖對照顯示。以 `py_compile` 驗證語法通過。
- 2026-07-29：檔案由使用者搬移並整併至 `AI_img/影像捲積.py`，新增範例圖片 `蒙娜麗莎.JPG`，`path` 改指向 `Ai_img/蒙娜麗莎.jpg`。
  - 備註：路徑大小寫（`Ai_img` vs 實際資料夾 `AI_img`）與副檔名大小寫（`.jpg` vs 實際 `.JPG`）在 Windows 檔案系統下不分大小寫，目前可正常執行；若未來搬到 Linux/Mac 或雲端環境會需要改成完全相符的大小寫。
- 2026-07-29：建立本檔案 `Agent.md`，作為此資料夾的執行動作與歷史紀錄索引。
- 2026-07-29：檔案第一行補上 `# -*- coding: utf-8 -*-` 明確編碼宣告；確認 `影像捲積.py` 本身為 UTF-8（無 BOM），未發現實際編碼錯誤。
- 2026-07-29：修正輸出視窗標題「原始圖片」「卷積後圖片」顯示成方框（豆腐字）的問題 — 根因是 matplotlib 預設字型不含中文字形，非程式邏輯錯誤。修法：加入 `plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"]` 與 `plt.rcParams["axes.unicode_minus"] = False`。已用 Agg backend 離線渲染驗證中文標題正常顯示。
- 2026-07-29：補完 `Module.py`（原本只有訓練超參數，未 import 任何深度學習框架）。確認需求後（框架＝PyTorch、資料集尚無印象、架構＝從零手刻簡單 CNN）新增：
  - `SimpleCNN`：3 層 (卷積 -> ReLU -> 池化)＋全連接分類頭，每層附上原理註解
  - `build_dataloaders()`：讀取 ImageFolder 格式資料集（子資料夾＝分類），切分訓練/驗證集
  - `train_one_epoch()` / `evaluate()`：標準 forward -> loss -> backward -> step 訓練迴圈
  - `DATA_DIR = ""`：資料集路徑先留空（使用者不確定原本作業用哪個資料集），需自行指向 ImageFolder 格式資料夾（例：`人物或物件識別/mask`，底下有「戴口罩」「沒戴口罩」子資料夾）
  - 已用 `py_compile` 驗證語法；並在 scratchpad 建立 2 類別×6 張的合成假資料集，跑過一次完整 dataloader → forward → backward → 更新參數的流程確認可執行成功（未動到專案內任何真實資料），測試完即刪除。
- 2026-07-29：使用者將 `Module.py` 搬移到新建的 `AI_img/CNN/` 子資料夾。撰寫 `AI_img/CNN/README.md`，整理這份 CNN 學習內容的核心重點與資料集學習資訊：
  - 核心重點：卷積、池化、全連接、ReLU、Dropout、CrossEntropyLoss、forward→loss→backward→step 訓練迴圈，以及各超參數（`Epchs`/`Batch_Size`/`lr`/`Img_Size`/`seed`）的意義，並對照 `影像捲積.py` 的手刻卷積說明兩者原理相通之處
  - 資料集學習資訊：說明 `ImageFolder` 資料夾格式規範（子資料夾＝分類），列出 repo 內現成候選資料集 `人物或物件識別/mask`（戴口罩/沒戴口罩）供使用者確認是否採用
  - 附上執行方式與如何解讀輸出的 loss / accuracy（含 overfitting 判斷提示）
