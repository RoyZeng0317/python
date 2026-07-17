# 安裝說明

本資料夾（`人臉識別.py`、`即時識別.py`）需要 OpenCV 才能執行人臉偵測。

## 需要安裝的套件

```powershell
pip install opencv-python==4.10.0.84
```
mediapipe
```powershell
pip install mediapipe
```
`numpy` 會被 `opencv-python` 當作相依套件一併自動安裝，不用另外裝。

## 為什麼要指定版本 4.10.0.84，不能直接 `pip install opencv-python`？

目前 PyPI 上最新的 `opencv-python 5.0.0.93` 是不完整的版本：

- `cv2` 模組裡完全沒有 `CascadeClassifier`（人臉偵測必備的類別）
- `cv2/data/` 資料夾沒有附帶任何 `haarcascade_*.xml` 模型檔

導致 `face_cascade = cv2.CascadeClassifier(...)` 這行會直接報錯
`AttributeError: module 'cv2' has no attribute 'CascadeClassifier'`。

改裝 `4.10.0.84`（穩定版）就會完整附上 `CascadeClassifier` 與所有 `haarcascade_*.xml` 檔案，程式碼不用修改。

已驗證此版本在 Python 3.14 下有現成的 wheel（`cp37-abi3`，可跨版本相容），不需要編譯。

## 驗證安裝是否成功

```powershell
python -c "import cv2; print(cv2.__version__); print(hasattr(cv2, 'CascadeClassifier'))"
```

應該輸出：

```
4.10.0
True
```

## 執行

```powershell
# 對單張圖片做人臉偵測（需先把要辨識的圖片放在同一資料夾，並修改檔名）
python 人臉識別.py

# 即時攝影機人臉偵測（需要接攝影機），按 q 鍵離開
python 即時識別.py
```
