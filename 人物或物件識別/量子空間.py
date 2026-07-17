import os
import random
import cv2
import numpy as np
import mediapipe as mp

# 這個 mediapipe build(0.10.35, Python 3.14)沒有 solutions 跟 framework 子模組,
# 只剩 tasks API,所以偵測手勢的關節資料改用 tasks API 自己解析,不能靠
# mediapipe.solutions.drawing_utils / hands_connections。

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

# 偵測手掌設定(參考影片的效果只用一隻手控制鏡頭,偵測 1 隻手就夠,效能也比較好)
options = HLP(
    num_hands=1,
    base_options=BO(model_asset_buffer=model_bytes),
    running_mode=VRM.IMAGE)

# ===== 3D 粒子星球 + 雙層光環 =====
# 仿照參考影片裡實際用的 Gemini prompt:
# 「由大量球形小粒子構成的橙色星球,表面聚集較多粒子;周圍環繞白色粒子構成兩層光環;
#   攝影機一直看著星球中心,用手勢控制攝影機旋轉/縮放」
PLANET_RADIUS = 120.0
NUM_PLANET_PARTICLES = 1400
NUM_RING_PARTICLES = 900
RING_BANDS = ((1.4, 1.55), (1.75, 1.95))   # 兩層光環的半徑範圍(相對於星球半徑倍數)
RING_TILT = 0.35                            # 光環傾斜角度(弧度),讓它看起來像土星環

def _generate_planet_points():
    pts = np.empty((NUM_PLANET_PARTICLES, 4), dtype='float64')
    for i in range(NUM_PLANET_PARTICLES):
        u, v = random.random(), random.random()
        theta = 2 * np.pi * u
        phi = np.arccos(2 * v - 1)
        # 半徑偏向球殼表面(平方讓分布更靠近外殼),符合「表面聚集較多粒子」的要求
        r = PLANET_RADIUS * (0.80 + 0.20 * random.random() ** 2)
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        pts[i] = (x, y, z, random.uniform(0.55, 1.0))
    return pts

def _generate_ring_points():
    pts = np.empty((NUM_RING_PARTICLES, 4), dtype='float64')
    cos_t, sin_t = np.cos(RING_TILT), np.sin(RING_TILT)
    for i in range(NUM_RING_PARTICLES):
        band = RING_BANDS[random.randrange(2)]
        r = PLANET_RADIUS * random.uniform(*band)
        theta = random.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        z = r * np.sin(theta)
        y = random.uniform(-1, 1) * PLANET_RADIUS * 0.02   # 環的厚度
        y, z = y * cos_t - z * sin_t, y * sin_t + z * cos_t  # 沿 X 軸把環傾斜一個角度
        pts[i] = (x, y, z, random.uniform(0.7, 1.0))
    return pts

PLANET_POINTS = _generate_planet_points()
RING_POINTS = _generate_ring_points()
PLANET_COLOR = (30, 150, 255)   # BGR,橙色星球
RING_COLOR = (235, 235, 235)    # BGR,白色光環

# ===== 攝影機狀態(由手勢驅動)=====
FOCAL_LENGTH = 480.0
MIN_CAMERA_DISTANCE = 260.0
MAX_CAMERA_DISTANCE = 950.0
IDLE_ROTATE_SPEED = 0.006        # 沒偵測到手時的緩慢自轉,避免畫面死掉
FIST_RAMP_FRAMES = 30            # 拳頭握住多久後達到最快退遠速度(先慢後快)
FIST_MAX_STEP = 16.0
OPEN_APPROACH_RATE = 0.10        # 五指張開時,朝最小距離逼近的比例(自然形成先快後慢)

camera_azimuth = 0.0
camera_distance = 560.0
fist_hold_frames = 0
prev_hand_angle = None

# ===== 手勢判斷(拇指以外 4 指的指尖/PIP 關節編號)=====
FINGER_TIP_PIP = ((8, 6), (12, 10), (16, 14), (20, 18))
WRIST = 0
MIDDLE_MCP = 9
MIDDLE_TIP = 12

def _dist(a, b):
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))

def is_fist(points):
    wrist = points[WRIST]
    curled = sum(1 for tip, pip in FINGER_TIP_PIP if _dist(points[tip], wrist) < _dist(points[pip], wrist))
    return curled >= 3

def is_open_hand(points):
    wrist = points[WRIST]
    extended = sum(1 for tip, pip in FINGER_TIP_PIP if _dist(points[tip], wrist) > _dist(points[pip], wrist) * 1.15)
    return extended >= 4

def hand_orientation_angle(points):
    # 手腕(0)指向中指根部(9)的方向,代表手掌目前朝向哪個角度,拿來偵測「旋轉手」的手勢
    wx, wy = points[WRIST]
    mx, my = points[MIDDLE_MCP]
    return np.arctan2(my - wy, mx - wx)

def update_camera(hands_points):
    global camera_azimuth, camera_distance, fist_hold_frames, prev_hand_angle
    if not hands_points:
        camera_azimuth += IDLE_ROTATE_SPEED   # 沒有手的時候讓星球緩慢自轉,畫面不會呆掉
        fist_hold_frames = 0
        prev_hand_angle = None
        return None

    points = hands_points[0]   # 只用偵測到的第一隻手控制鏡頭

    # 手勢旋轉 → 攝影機環繞角度
    angle = hand_orientation_angle(points)
    if prev_hand_angle is not None:
        delta = angle - prev_hand_angle
        delta = (delta + np.pi) % (2 * np.pi) - np.pi   # 修正繞過 -pi/pi 邊界的跳動
        camera_azimuth += delta
    prev_hand_angle = angle

    gesture = 'none'
    if is_fist(points):
        # 握拳 → 攝影機拉遠,持續握住的時間越久,退遠速度越快(先慢後快)
        gesture = 'fist (zoom out)'
        fist_hold_frames += 1
        ramp = min(fist_hold_frames / FIST_RAMP_FRAMES, 1.0)
        camera_distance = min(MAX_CAMERA_DISTANCE, camera_distance + FIST_MAX_STEP * ramp)
    else:
        fist_hold_frames = 0
        if is_open_hand(points):
            # 五指張開 → 攝影機朝最小距離逼近,離目標越遠移動越快(先快後慢)
            gesture = 'open (zoom in)'
            camera_distance += (MIN_CAMERA_DISTANCE - camera_distance) * OPEN_APPROACH_RATE
            camera_distance = max(MIN_CAMERA_DISTANCE, camera_distance)
    return gesture

def project_points(points_3d):
    cos_a, sin_a = np.cos(camera_azimuth), np.sin(camera_azimuth)
    x, y, z = points_3d[:, 0], points_3d[:, 1], points_3d[:, 2]
    xr = x * cos_a - z * sin_a       # 繞 Y 軸環繞星球中心(等同於攝影機繞著星球轉)
    zr = x * sin_a + z * cos_a
    depth = np.clip(zr + camera_distance, 1e-3, None)
    scale = FOCAL_LENGTH / depth
    return xr * scale, y * scale, zr, scale

def draw_point_cloud(canvas, points_4d, base_color):
    w, h = canvas.shape[1], canvas.shape[0]
    sx, sy, zr, scale = project_points(points_4d[:, :3])
    brightness = points_4d[:, 3]
    b, g, r = base_color
    order = np.argsort(-zr)   # 由遠到近畫(painter's algorithm),近的粒子蓋在遠的上面
    cx, cy = w / 2, h / 2
    for i in order:
        x = cx + sx[i]
        y = cy - sy[i]
        if 0 <= x < w and 0 <= y < h and scale[i] > 0.05:
            radius = max(1, int(1.6 * scale[i]))
            fade = float(brightness[i])
            cv2.circle(canvas, (int(x), int(y)), radius,
                       (int(b * fade), int(g * fade), int(r * fade)), -1)

def render_planet_scene(camera_frame, detection_result):
    height, width = camera_frame.shape[:2]
    canvas = np.zeros((height, width, 3), dtype='uint8')

    hands_points = [
        [(int(lm.x * width), int(lm.y * height)) for lm in hand_landmarks]
        for hand_landmarks in detection_result.hand_landmarks
    ]
    gesture = update_camera(hands_points)

    glow = np.zeros_like(canvas)
    draw_point_cloud(glow, RING_POINTS, RING_COLOR)
    draw_point_cloud(glow, PLANET_POINTS, PLANET_COLOR)
    glow = cv2.GaussianBlur(glow, (9, 9), 0)
    canvas = cv2.add(canvas, glow)
    draw_point_cloud(canvas, RING_POINTS, RING_COLOR)
    draw_point_cloud(canvas, PLANET_POINTS, PLANET_COLOR)

    # 左上角小小顯示目前鏡頭狀態,方便確認手勢有沒有被辨識到(參考影片右下角的攝影機小視窗改放這裡)
    cv2.putText(canvas, f"gesture: {gesture or 'none'}  dist: {camera_distance:.0f}",
                (14, 28), cv2.FONT_HERSHEY_DUPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
    thumb_h, thumb_w = height // 5, width // 5
    thumbnail = cv2.resize(camera_frame, (thumb_w, thumb_h))
    canvas[height - thumb_h - 10:height - 10, width - thumb_w - 10:width - 10] = thumbnail
    return canvas

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

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   # mediapipe 要 RGB,frame 原本是 BGR
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        hand_landmarker_result = landmarker.detect(mp_img)

        annotated = render_planet_scene(frame, hand_landmarker_result)
        cv2.imshow('quantum planet', annotated)
        if cv2.waitKey(5) in (ord('q'), ord('Q')):
            break
cap.release()
cv2.destroyAllWindows()
