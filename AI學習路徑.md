# AI 學習路徑

整理 repo 內現有 AI 相關程式，依難度由易到難排序，方便按順序複習與練習。

## 第一階段：基礎工具

| 檔案 | 學什麼 |
|---|---|
| `learning/numpy/basic_numpuy.py` | numpy 陣列運算基礎 |
| `learning/matplotlib/basic_matplotlib.py` | 資料視覺化基礎（畫圖表） |
| `learning/tkinter/mini_tkinter.py` | GUI 基礎，之後 CNN/YOLO 想做互動介面會用到 |
| `learning/flask/` | web 後端基礎（目前為空，可搭配 AI/week1/Day6 一起看） |

## 第二階段：AI 課程回顧（`AI/week1`、`AI/week2`）

依 Day 資料夾順序複習：
- **Day2**：Python 基本語法、if/else、bool、簡單物理計算
- **Day3**：for/while loop、list、matplotlib 折線圖/直方圖/散步圖、人口統計實戰
- **Day4**：GUI 練習
- **Day5**：socket 聊天室（`chatServer.py` / `chatclient.py`）
- **Day6**：簡易 web 專案（api_design.md + html/css/js + view.py，購物車練習）
- **Day9~Day10**：銜接到 YOLO 推論，是進入第五階段前的橋接

## 第三階段：影像處理原理

`AI_img/影像捲積.py` — 手刻 2D 卷積 (`convolve2d`)，不靠框架、自己理解 CNN 卷積層在做什麼運算，是看懂第五階段 CNN 的前置知識。

## 第四階段：手寫數字辨識

`AI_img/手寫數字/`（`tranning.py` 訓練、`即時手寫.py` 即時辨識、`model.pth` 已訓練好的模型）＋根目錄 `MNIST/raw` 資料集。用 PyTorch 做最基礎的影像分類，是進 CNN 前的暖身。

## 第五階段：CNN 進階（`AI_img/CNN/`）

從零手刻 `SimpleCNN`（卷積→ReLU→池化→全連接），`README.md` 已完整整理卷積、池化、Dropout、損失函數、訓練迴圈（forward→loss→backward→step）等原理，直接讀那份 README 最快。

已實測跑通：`DATA_DIR` 指向 `人物或物件識別/mask`（口罩偵測二分類，實際只有 35 張圖片），5 epoch 後 train_acc 0.46→0.64、val_acc 卡在 0.43（資料量太小、僅供跑通流程，非有意義的準確率）。`mask/` 底下混了 `.venv`／`__pycache__` 兩個非分類資料夾，已在 `Module.py` 用 `CleanImageFolder` 覆寫 `find_classes` 濾掉，避免被當成訓練分類。

## 第六階段：物件偵測與追蹤（`yolo/`）

檔名已經照學習順序編號，直接照 05→10 做下去即可：
1. `05_訓練我的 yolo11n.py` — 訓練 YOLO11 模型
2. `06_評估訓練結果.py` — 評估準確率
3. `07_自動訓練模型推論.py` — 用訓練好的模型推論
4. `08_webcam串流推論.py` — 即時攝影機推論
5. `09_CCTV.py` — 監控串流應用
6. `10_物件追蹤與計數.py` — 多物件追蹤與計數（進階）

## 第七階段：實戰整合（`人物或物件識別/`）

前面學的技術綜合應用：`人臉識別.py`、`偵測手掌數據.py`、`即時識別.py`、`即時汽車識別系統.py`、`opencv 多物件追蹤.py`、`3D粒子手勢.py`（手勢辨識＋3D 視覺化，難度最高）。`install.md` 有安裝說明，`README.md` 列出需要的套件（opencv-python、pillow）。

## 建議下一步

第五階段的訓練已跑通，串起第三～五階段。接下來可以進 `yolo/` 系列（第六階段）；如果想讓口罩偵測有實際準確率，需要先補資料（目前只有 35 張）。想練新技能（語音辨識、聊天機器人等 repo 目前沒有的類型）之後可以再另外規劃。
