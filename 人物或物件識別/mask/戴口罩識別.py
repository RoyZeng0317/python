# enivorment
# pip install opencv-python
# pip install tensorflow
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
from PIL import ImageFont, ImageDraw, Image  # 載入 PIL 相關函式庫

fontpath = 'NotoSansTC-Regular.ttf'          # 設定字型路徑

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("keras_Model.h5", compile=False)

def text(text):                               # 建立顯示文字的函式
    global show_img                           # 設定 img 為全域變數
    org = (0,50)                              # 文字位置
    font = ImageFont.truetype(fontpath, 50)   # 設定字型與文字大小
    imgPil = Image.fromarray(show_img)        # 將 img 轉換成 PIL 影像
    draw = ImageDraw.Draw(imgPil)             # 準備開始畫畫
    draw.text((0, 0), text, fill=(255, 255, 255), font=font)  # 寫入文字
    show_img = np.array(imgPil)  

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break
    img = cv2.resize(frame , (398, 224))
    show_img = img[0:224, 80:304]

    img = np.asarray(show_img, dtype=np.float32).reshape(1, 224, 224, 3)
    img = (img / 127.5) - 1

    prediction = model.predict(img)
    index = np.argmax(prediction)
    print(index)
    if index == 0:
        text('疑似偷竊者')  # 使用 text() 函式，顯示文字
    elif index == 1:
        text('一般民眾')
    cv2.imshow("Webcam Image", show_img)

    if cv2.waitKey(1) == ord('q'):
        break    # 按下 q 鍵停止
cap.release()
cv2.destroyAllWindows()