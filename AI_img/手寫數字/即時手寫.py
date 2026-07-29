import os
import sys
import time
import urllib.request
from types import SimpleNamespace

import cv2
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pth")
HAND_MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
HAND_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

sys.path.insert(0, BASE_DIR)
from tranning import Net  # 重用訓練時定義的網路結構

# MediaPipe 手部關鍵點編號
INDEX_TIP, INDEX_PIP = 8, 6
MIDDLE_TIP, MIDDLE_PIP = 12, 10

PAUSE_SECONDS = 5.0        # 手指停頓超過幾秒後觸發辨識
MOVE_THRESHOLD = 4         # 移動超過幾像素才視為新的筆畫（過濾手震雜訊）
LINE_THICKNESS = 12
BUTTON_SIZE = (140, 56)    # 開始/暫停按鈕大小
# OpenCV 在 Windows 上的視窗標題（HighGUI）只支援 ANSI 編碼，中文會顯示亂碼，
# 且無法像畫面內容一樣用字型修正，因此視窗標題固定用英文，中文標題改畫在畫面左上角。
WINDOW_NAME = "Realtime Handwritten Digit Recognition (q=quit)"
TITLE_TEXT = "即時手寫數字辨識"

# 中文字型（Windows 內建），找不到就退回內建字型（無法顯示中文，但不會壞掉）
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msjh.ttc",
    r"C:\Windows\Fonts\mingliu.ttc",
    r"C:\Windows\Fonts\kaiu.ttf",
]
_FONT_CACHE = {}

# matplotlib 預設字型（DejaVu Sans）不含中文字形，plt.title() 等中文文字會變成方框。
# 註冊同一套中文字型讓 plt.show() 顯示的辨識結果也能正確顯示中文。
_cjk_font_path = next((p for p in _FONT_CANDIDATES if os.path.exists(p)), None)
if _cjk_font_path:
    font_manager.fontManager.addfont(_cjk_font_path)
    _cjk_font_name = font_manager.FontProperties(fname=_cjk_font_path).get_name()
    plt.rcParams["font.sans-serif"] = [_cjk_font_name]
    plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.unicode_minus"] = False


def _load_font(size: int):
    if size not in _FONT_CACHE:
        for path in _FONT_CANDIDATES:
            if os.path.exists(path):
                _FONT_CACHE[size] = ImageFont.truetype(path, size)
                break
        else:
            _FONT_CACHE[size] = ImageFont.load_default()
    return _FONT_CACHE[size]


def put_chinese_text(frame_bgr, text, org, font_size=28, color_bgr=(255, 255, 255)):
    """cv2.putText 不支援中文字形，改用 PIL 只轉換文字所在的小範圍來畫中文。"""
    x, y = org
    box_w = font_size * len(text) + 16
    box_h = font_size + 16
    x2 = min(x + box_w, frame_bgr.shape[1])
    y2 = min(y + box_h, frame_bgr.shape[0])
    if x2 <= x or y2 <= y:
        return frame_bgr

    roi = frame_bgr[y:y2, x:x2]
    img_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    color_rgb = (color_bgr[2], color_bgr[1], color_bgr[0])
    draw.text((8, 8), text, font=_load_font(font_size), fill=color_rgb)
    frame_bgr[y:y2, x:x2] = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return frame_bgr


def draw_toggle_button(frame_bgr, paused: bool):
    """畫出開始/暫停切換鈕（同一顆按鈕依狀態切換文字），回傳按鈕範圍供點擊判斷。"""
    w = frame_bgr.shape[1]
    bw, bh = BUTTON_SIZE
    x1, y1 = w - bw - 10, 10
    x2, y2 = x1 + bw, y1 + bh
    cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (40, 40, 40), -1)
    cv2.rectangle(frame_bgr, (x1, y1), (x2, y2), (255, 255, 255), 2)
    label = "開始" if paused else "暫停"
    put_chinese_text(frame_bgr, label, (x1 + 30, y1 + 6), font_size=26, color_bgr=(255, 255, 255))
    return (x1, y1, x2, y2)


def load_digit_model() -> Net:
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"找不到模型檔案：{MODEL_PATH}\n請先執行 tranning.py 完成訓練並產生 model.pth"
        )
    net = Net()
    net.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    net.eval()
    return net


def ensure_hand_model() -> str:
    if not os.path.exists(HAND_MODEL_PATH):
        print("首次執行，正在下載手部追蹤模型...")
        urllib.request.urlretrieve(HAND_MODEL_URL, HAND_MODEL_PATH)
        print("手部追蹤模型下載完成：", HAND_MODEL_PATH)
    return HAND_MODEL_PATH


def create_hand_landmarker():
    # 用 model_asset_buffer（讀入記憶體）而非 model_asset_path：
    # mediapipe 在 Windows 上讀取含中文（非 ASCII）路徑的模型檔會失敗（errno=-1）。
    with open(ensure_hand_model(), "rb") as f:
        model_bytes = f.read()

    options = vision.HandLandmarkerOptions(
        base_options=BaseOptions(model_asset_buffer=model_bytes),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.5,
    )
    return vision.HandLandmarker.create_from_options(options)


def preprocess_canvas(canvas: np.ndarray):
    """把畫布上的筆畫裁切、置中、縮放成 MNIST 格式的 28x28 灰階圖。"""
    ys, xs = np.where(canvas > 0)
    if len(xs) == 0:
        return None

    pad = 20
    x1, x2 = max(int(xs.min()) - pad, 0), min(int(xs.max()) + pad, canvas.shape[1])
    y1, y2 = max(int(ys.min()) - pad, 0), min(int(ys.max()) + pad, canvas.shape[0])
    digit = canvas[y1:y2, x1:x2]

    side = max(digit.shape)
    square = np.zeros((side, side), dtype=np.uint8)
    y_off = (side - digit.shape[0]) // 2
    x_off = (side - digit.shape[1]) // 2
    square[y_off:y_off + digit.shape[0], x_off:x_off + digit.shape[1]] = digit

    return cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA)


def predict_digit(net: Net, digit_img: np.ndarray) -> int:
    tensor = torch.from_numpy(digit_img).float() / 255.0
    with torch.no_grad():
        output = net.forward(tensor.view(-1, 28 * 28))
    return int(torch.argmax(output))


def show_result(digit_img: np.ndarray, prediction: int) -> None:
    plt.figure("辨識結果")
    plt.imshow(digit_img, cmap="gray")
    plt.title(f"辨識結果：{prediction}")
    plt.axis("off")
    plt.show()  # 單獨顯示辨識結果


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def main():
    net = load_digit_model()
    landmarker = create_hand_landmarker()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("無法開啟攝影機")

    print("使用方式：")
    print(" - 只伸出食指＝書寫模式（畫線）")
    print(" - 食指＋中指一起伸出＝移動模式（提筆移動，不畫線，用來換到下一筆畫）")
    print(" - 停頓超過 5 秒會自動送出辨識，辨識後自動清除畫面")
    print(" - 右上角按鈕可暫停／繼續（暫停時不追蹤、不計時）")
    print(" - 按 q 或 ESC 離開")

    state = SimpleNamespace(paused=False)
    button_rect: list[tuple[int, int, int, int] | None] = [None]  # 用可變容器讓 mouse callback 讀到最新的按鈕範圍

    def on_mouse(event, x, y, flags, param):
        rect = button_rect[0]
        if rect is None or event != cv2.EVENT_LBUTTONDOWN:
            return
        x1, y1, x2, y2 = rect
        if x1 <= x <= x2 and y1 <= y <= y2:
            state.paused = not state.paused

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    canvas = None
    draw_point = None    # 上一個「書寫模式」座標，用來連成線
    track_point = None   # 上一個偵測到的原始座標，只用來判斷有沒有停頓
    last_move_time = time.time()
    frame_index = 0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)  # 水平翻轉，符合鏡像直覺
            h, w = frame.shape[:2]

            if canvas is None:
                canvas = np.zeros((h, w), dtype=np.uint8)

            if not state.paused:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                frame_index += 1
                result = landmarker.detect_for_video(mp_image, frame_index)

                if result.hand_landmarks:
                    landmarks = result.hand_landmarks[0]
                    tip = landmarks[INDEX_TIP]
                    point = (int(tip.x * w), int(tip.y * h))

                    index_up = landmarks[INDEX_TIP].y < landmarks[INDEX_PIP].y
                    middle_up = landmarks[MIDDLE_TIP].y < landmarks[MIDDLE_PIP].y
                    drawing = index_up and not middle_up  # 只伸食指＝下筆

                    moved = track_point is None or _dist(point, track_point) > MOVE_THRESHOLD
                    if moved:
                        last_move_time = time.time()
                        track_point = point

                    if drawing:
                        if draw_point is not None and moved:
                            cv2.line(canvas, draw_point, point, 255, LINE_THICKNESS)
                        draw_point = point
                        dot_color = (0, 0, 255)   # 紅點：書寫中
                    else:
                        draw_point = None         # 提筆：切斷連線，可移動到下一筆畫起點
                        dot_color = (0, 255, 0)   # 綠點：移動中（不畫線）

                    cv2.circle(frame, point, 8, dot_color, -1)
                else:
                    draw_point = None
                    track_point = None
            else:
                last_move_time = time.time()  # 暫停時凍結計時，避免恢復後立刻誤觸發辨識

            # 手寫筆畫疊加在攝影機畫面上，讓使用者確認是否成功寫入
            display = frame.copy()
            display[canvas > 0] = (0, 255, 255)
            put_chinese_text(display, TITLE_TEXT, (10, 8), font_size=22, color_bgr=(255, 255, 255))
            button_rect[0] = draw_toggle_button(display, state.paused)

            has_ink = bool(np.any(canvas > 0))
            if not state.paused and has_ink and (time.time() - last_move_time) >= PAUSE_SECONDS:
                put_chinese_text(display, "識別中...", (10, 42), font_size=30, color_bgr=(0, 0, 255))
                cv2.imshow(WINDOW_NAME, display)
                cv2.waitKey(1)

                digit_img = preprocess_canvas(canvas)
                canvas[:] = 0  # 清除手寫
                draw_point = None
                track_point = None
                last_move_time = time.time()

                if digit_img is not None:
                    prediction = predict_digit(net, digit_img)
                    show_result(digit_img, prediction)
                continue

            cv2.imshow(WINDOW_NAME, display)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):  # q 或 ESC 離開
                break
    finally:
        landmarker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
