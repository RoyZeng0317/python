# 需求
延續 AI 課程作業的記憶：用 CNN (卷積神經網路) 做影像分類，並且要理解每一步背後的原理，不是只會呼叫框架。
框架：PyTorch。模型：從零手刻的簡單 CNN（非直接套用預訓練模型）。

# 核心重點（原理）

## 1. 卷積層 Convolution (`nn.Conv2d`)
- 用一個小範圍的濾波器 (kernel，例如 3x3) 在圖片上滑動，每個位置做「逐元素相乘後加總」，抽取局部特徵。
- 淺層抓邊緣、顏色等低階特徵；疊多層後，深層能組合成紋理、形狀、甚至接近物件輪廓的高階特徵。
- `padding=1` 讓輸出的長寬和輸入一致，避免每卷一次圖就變小一圈。
- 對應 `AI_img/影像捲積.py` 手刻的 `convolve2d()` 就是同一個運算原理，只是這裡改由 PyTorch 的 `Conv2d` 自動處理，且 kernel 權重是「學出來的」而不是像影像捲積那樣自己指定。

## 2. 池化層 Pooling (`nn.MaxPool2d`)
- 把特徵圖邊長縮小一半（取每個 2x2 區塊的最大值），保留主要特徵、降低運算量。
- 讓模型對物體些微的位移、變形更穩健（不會因為物體移動一點點就完全認不出來）。

## 3. 全連接層 Fully Connected (`nn.Linear`)
- 把最後一層卷積/池化後的特徵圖「攤平」成一維向量，交給全連接層做最終分類判斷。
- 輸出的數字（logits）代表每個類別的分數，數值最大的類別就是模型的預測結果。

## 4. 激活函數 ReLU
- 每次卷積/線性運算後都接一個 ReLU（負數變 0，正數不變），替模型加入非線性，才能學到複雜的規律，而不是只能疊加出直線關係。

## 5. Dropout
- 訓練時隨機關閉一部分神經元，避免模型「死記」訓練資料（過度擬合 overfitting），逼模型學到比較通用的特徵。

## 6. 損失函數 Loss (`CrossEntropyLoss`)
- 衡量模型預測分數和正確答案之間差多少，是多分類問題最常用的損失函數。

## 7. 訓練迴圈：forward → loss → backward → step
1. `forward`：圖片丟進模型，算出預測分數
2. `loss`：用 CrossEntropyLoss 算出預測跟正確答案的誤差
3. `backward`：反向傳播，自動算出「每個參數該往哪個方向調整」的梯度
4. `step`：optimizer（這裡用 Adam）依梯度更新參數，讓下一次的 loss 更小
- 每跑完一輪完整資料集稱為一個 **epoch**。

## 8. 超參數（`Module.py` 開頭定義）
| 變數 | 意義 |
|---|---|
| `Epchs` | 要訓練幾輪（原始拼字保留，未更動變數名稱） |
| `Batch_Size` | 一次丟進模型幾張圖片一起算 |
| `lr` | learning rate 學習率，決定每次參數更新的步伐大小 |
| `Img_Size` | 圖片統一縮放成幾 x 幾像素再丟進模型 |
| `seed` | 亂數種子，固定後每次切分訓練/驗證集的結果才能重現 |

# 資料集學習資訊

## 格式要求：ImageFolder
PyTorch 的 `torchvision.datasets.ImageFolder` 規定資料夾結構如下，資料夾名稱就是類別名稱：
```
DATA_DIR/
├── 類別A/
│   ├── 001.jpg
│   └── 002.jpg
└── 類別B/
    ├── 001.jpg
    └── 002.jpg
```
不需要另外寫標籤檔，`ImageFolder` 會自動把子資料夾名稱轉成分類標籤。

## 目前狀態
`Module.py` 的 `DATA_DIR = ""` 還是空的 —— 因為不確定當初作業指定的是哪個資料集。

repo 裡現成、格式剛好符合 ImageFolder 的候選資料集：
- `人物或物件識別/mask/戴口罩/`、`人物或物件識別/mask/沒戴口罩/` — 二分類（口罩偵測），實際只有 35 張圖片（戴口罩 17 張、沒戴口罩 18 張），資料量很小，只夠跑通流程、不足以訓練出準確的模型。
- 注意：`人物或物件識別/mask/` 底下還有 `.venv`、`__pycache__` 這兩個非分類資料夾，`ImageFolder` 預設會把它們也當成分類，`Module.py` 已用 `CleanImageFolder`（覆寫 `find_classes`）濾掉。

已把 `DATA_DIR` 指向 `../../人物或物件識別/mask` 並實測跑完 5 epoch：train_acc 從 0.46 升到 0.64，但 val_acc 卡在 0.43 沒動——這是資料量太小（驗證集只有 7 張）的正常現象，不是程式錯誤。想要有意義的準確率，之後需要補更多資料，或改用預訓練模型做遷移學習（transfer learning）取代從零訓練。

# 檔案結構
- `Module.py` — CNN 模型與訓練程式主體
  - `SimpleCNN` — 3 層 (卷積 → ReLU → 池化) + 全連接分類頭
  - `build_dataloaders()` — 讀 ImageFolder 資料集、切訓練/驗證集
  - `train_one_epoch()` / `evaluate()` — 訓練與驗證迴圈
  - `if __name__ == "__main__":` — 設定隨機種子、建立模型、跑 `Epchs` 輪訓練並印出每輪的 loss / accuracy

# 使用方式
```powershell
# 先把 Module.py 的 DATA_DIR 改成實際資料集路徑，例如：
# DATA_DIR = "../../人物或物件識別/mask"
cd AI_img/CNN
python Module.py
```
執行後每個 epoch 會印出：
```
Epoch 1/5 | train_loss=... train_acc=... | val_loss=... val_acc=...
```
- **loss 越低越好**：代表預測跟正確答案越接近
- **accuracy 越高越好**：代表分類正確的比例越高
- 如果 train_acc 一直上升但 val_acc 停滯或下降，代表模型開始過度擬合 (overfitting)
