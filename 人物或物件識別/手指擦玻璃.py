import cv2
import mediapipe as mp
import numpy as np
import math

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode

# 新版 mediapipe(Python 3.14 對應的 0.10.35)已移除舊版 mp.solutions.hands,
# 改用 Tasks API,需要 hand_landmarker.task 模型檔(已下載到本檔案同一層)
hand_options = HandLandmarkerOptions(
    base_options = BaseOptions(model_asset_path = 'hand_landmarker.task'),
    running_mode = VisionTaskRunningMode.VIDEO,
    num_hands = 2,
    min_hand_detection_confidence = 0.5,
    min_tracking_confidence = 0.5
)

cap = cv2.VideoCapture(0) # read the camera

# mediapipe 啟用偵測手掌
with HandLandmarker.create_from_options(hand_options) as hands:
    if not cap.isOpened():
        print("Can't open camera")
        exit()
    w = 640 # 定義影像寬度
    h = 360 # 定義影像高度
    dots = [] # record 座標
    mask_b = np.zeros((h, w, 3), dtype='uint8')     # 產生黑色遮罩 -> 套用清楚影像
    mask_w = np.zeros((h, w, 3), dtype='uint8')     # 產生白色遮罩 -> 套用模糊影像
    mask_w[0:h, 0:w] = 255
    frame_idx = 0 # detect_for_video 需要遞增的時間戳記(毫秒)

    while True:
        ret, img = cap.read()
        if not ret:
            print("Can't receive frame")
            break
        img = cv2.resize(img, (w, h))                       # 縮小尺寸，加快處理效率
        img = cv2.flip(img, 1)                              # 翻轉影像
        img_hand = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)     # 偵測手勢用(新版 API 需要 RGB 3 channel)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)         # 轉換顏色為 BGRA (計算時需要用到 Alpha 色板)
        img2 = cv2.blur(img, (55, 55))                      # 套用模糊

        mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = img_hand)
        results = hands.detect_for_video(mp_image, int(frame_idx * (1000 / 30)))  # 偵測手勢
        frame_idx += 1
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                finger_points = []                           # 紀錄手指節點位置串列
                for i in hand_landmarks:
                    x = i.x
                    y = i.y
                    finger_points.append((x, y))            # 紀錄手指節點位置
                if finger_points:
                    fx1 = finger_points[8][0]
                    fy1 = finger_points[8][1]
                    fx2 = finger_points[12][0]
                    fy2 = finger_points[12][1]
                    d = ((fx1 - fx2) * (fx1 - fx2) + (fy1 - fy2) * (fy1 - fy2)) ** 0.5 # 計算食指與中指分開距離
                    if d < 0.15:
                        dots.append([fx1, fy1])
                        dl = len(dots)
                        x1 = int(dots[dl - 2][0] * w) # 計算出真正的座標
                        y1 = int(dots[dl - 2][1] * h)
                        x2 = int(dots[dl - 1][0] * w)
                        y2 = int(dots[dl - 1][1] * h)
                        cv2.line(mask_w, (x1, y1), (x2, y2), (0, 0, 0), 50)         # 在白色遮罩上畫出黑色線條
                        cv2.line(mask_b, (x1, y1), (x2, y2), (255, 255, 255), 50)   # 在黑色遮罩上畫出白色線條
                    else:
                        dots = []

        # 不管這一幀有沒有偵測到手,都要合成並顯示畫面,否則沒偵測到手時視窗永遠不會出現
        mask1 = cv2.cvtColor(mask_b, cv2.COLOR_BGR2GRAY)    # 轉換遮罩為灰階
        img = cv2.bitwise_and(img, img, mask=mask1)         # 清楚影像套用黑遮罩
        mask2 = cv2.cvtColor(mask_w, cv2.COLOR_BGR2GRAY)    # 轉換遮罩為灰階
        img2 = cv2.bitwise_and(img2, img2, mask=mask2)      # 模糊影像套用白遮罩

        output = cv2.add(img, img2)                         # 合併影像

        cv2.imshow('test', output)
        keyboard = cv2.waitKey(5)
        if keyboard == ord('q'):
            break
cap.release()
cv2.destroyAllWindows()