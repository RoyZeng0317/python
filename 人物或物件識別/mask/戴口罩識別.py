# enivorment
# pip install opencv-python
# pip install tensorflow tf-keras h5py
# .venv\Scripts\python.exe 戴口罩識別.py
import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'  # keras_Model.h5 is an old-format Teachable Machine export; Keras 3 can't load it
import h5py
from tensorflow.keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
from PIL import ImageFont, ImageDraw, Image  # 載入 PIL 相關函式庫

fontpath = r'C:\Windows\Fonts\msjh.ttc'      # 設定字型路徑(Windows 內建微軟正黑體,支援繁體中文)

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
# Loaded via an open h5py.File (not a path string) because Windows paths containing
# non-ASCII folder names crash TensorFlow's is_directory_v2 check on this TF/Keras version.
with h5py.File("keras_Model.h5", "r") as _f:
    model = load_model(_f, compile=False)

DISPLAY_SIZE = 640  # 顯示視窗大小(正方形邊長),要更大/更小直接改這個數字

def text(text):                               # 建立顯示文字的函式
    global show_img                           # 設定 img 為全域變數
    font_size = max(20, DISPLAY_SIZE // 12)   # 字型大小依顯示尺寸等比例縮放
    font = ImageFont.truetype(fontpath, font_size)   # 設定字型與文字大小
    imgPil = Image.fromarray(show_img)        # 將 img 轉換成 PIL 影像
    draw = ImageDraw.Draw(imgPil)             # 準備開始畫畫
    draw.text((0, 0), text, fill=(255, 255, 255), font=font)  # 寫入文字
    show_img = np.array(imgPil)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # 向攝影機要求較高擷取解析度(來源畫質好,放大才不糊)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

WINDOW_NAME = "Webcam Image"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)  # 讓視窗可被拖曳調整大小
cv2.resizeWindow(WINDOW_NAME, DISPLAY_SIZE, DISPLAY_SIZE)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break

    # 模型判斷用:維持 Teachable Machine 訓練時的 224x224 前處理,不影響畫面顯示畫質
    model_frame = cv2.resize(frame, (398, 224), interpolation=cv2.INTER_AREA)
    model_crop = model_frame[0:224, 80:304]
    model_input = np.asarray(model_crop, dtype=np.float32).reshape(1, 224, 224, 3)
    model_input = (model_input / 127.5) - 1

    # 畫面顯示用:直接從攝影機原始高解析度畫面裁切相同構圖範圍,再放大,避免用已經縮小的 224px 小圖硬拉伸
    fh, fw = frame.shape[:2]
    crop_x0, crop_x1 = int(fw * 80 / 398), int(fw * 304 / 398)
    show_img = cv2.resize(frame[:, crop_x0:crop_x1], (DISPLAY_SIZE, DISPLAY_SIZE), interpolation=cv2.INTER_CUBIC)

    prediction = model.predict(model_input)
    index = np.argmax(prediction)
    print(index)
    if index == 0:
        text('一般民眾')  # 使用 text() 函式，顯示文字
    elif index == 1:
        text('疑似偷竊者')
    cv2.imshow(WINDOW_NAME, show_img)

    if cv2.waitKey(1) == ord('q'):
        break    # 按下 q 鍵停止
cap.release()
cv2.destroyAllWindows()