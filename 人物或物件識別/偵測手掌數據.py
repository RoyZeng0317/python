# enivorment
# pip install mediapipe
import os
import cv2
import numpy as np
import mediapipe as mp

# 這個 mediapipe build(0.10.35, Python 3.14)沒有 solutions 跟 framework 子模組,
# 只剩 tasks API,所以畫骨架改成用 cv2 手動畫,不能靠 mediapipe.solutions.drawing_utils。
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),          # 大拇指
    (0, 5), (5, 6), (6, 7), (7, 8),          # 食指
    (5, 9), (9, 10), (10, 11), (11, 12),     # 中指
    (9, 13), (13, 14), (14, 15), (15, 16),   # 無名指
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),  # 小指 + 手掌
)

BO = mp.tasks.BaseOptions
HL = mp.tasks.vision.HandLandmarker
HLP = mp.tasks.vision.HandLandmarkerOptions
VRM = mp.tasks.vision.RunningMode

# 模型檔跟這支腳本放在同一層。注意:這個資料夾名稱含中文,
# mediapipe 在 Windows 上用 model_asset_path 讀取含中文的路徑時,底層 ctypes
# 呼叫會把路徑編碼弄亂(FileNotFoundError/亂碼路徑),所以改成用 Python 自己
# 讀檔案 bytes、透過 model_asset_buffer 傳進去,繞開這個路徑編碼問題。
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')
with open(MODEL_PATH, 'rb') as f:
    model_bytes = f.read()

# 偵測手掌設定
options = HLP(
    num_hands= 2,
    base_options=BO(model_asset_buffer=model_bytes),
    running_mode=VRM.IMAGE)
# 標記文字
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

# 繪製手掌骨架
def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    height, width, _ = annotated_image.shape
    points = [(int(landmark.x * width), int(landmark.y * height)) for landmark in hand_landmarks]
    for start, end in HAND_CONNECTIONS:
      cv2.line(annotated_image, points[start], points[end], (255, 255, 255), 2)
    for x, y in points:
      cv2.circle(annotated_image, (x, y), 4, HANDEDNESS_TEXT_COLOR, -1)

    # Get the top left corner of the detected hand's bounding box.
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image

with HL.create_from_options(options) as landmarker:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Can't open camera")
        exit()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame")
            break
        w = frame.shape[1]      # 畫面寬度
        h = frame.shape[0]      # 畫面高度

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   # mediapipe 要 RGB,frame 原本是 BGR
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        hand_landmarker_result = landmarker.detect(mp_img)

        print(hand_landmarker_result)

        annotated = draw_landmarks_on_image(frame, hand_landmarker_result)
        cv2.imshow('hand', annotated)
        if cv2.waitKey(5) in (ord('q'), ord('Q')):
            break
cap.release()
cv2.destroyAllWindows()