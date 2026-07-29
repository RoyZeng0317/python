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

# 偵測手掌設定(只用一隻手控制鏡頭跟切換造型,偵測 1 隻手就夠,效能也比較好)
options = HLP(
    num_hands=1,
    base_options=BO(model_asset_buffer=model_bytes),
    running_mode=VRM.IMAGE)

# =====================================================================
# 3D 粒子造型:比出 1~5 根手指切換羽球 / 海王星 / 冥王星 / 鑽石 / 寶箱
# 手掌旋轉角度 → 物件自轉;手掌靠近/遠離鏡頭 → 縮放距離
# =====================================================================

FOCAL_LENGTH = 480.0
MIN_CAMERA_DISTANCE = 250.0
MAX_CAMERA_DISTANCE = 900.0
IDLE_ROTATE_SPEED = 0.006      # 沒偵測到手時的緩慢自轉,避免畫面死掉
ZOOM_SMOOTH = 0.12             # 縮放用低通濾波,手放大小抖動不會讓畫面一直跳

# 手掌大小(手腕到中指根部的像素距離)對應鏡頭遠近的參考範圍。
# 這兩個數字跟攝影機解析度、手離鏡頭的距離有關,如果覺得縮放反應太鈍或太敏感,
# 可以依照自己的攝影機調整這兩個值。
PALM_SIZE_FAR = 45.0
PALM_SIZE_NEAR = 140.0

GESTURE_HOLD_FRAMES = 5        # 手指數要連續穩定這麼多幀,才會真的切換造型(避免手指過渡時誤判)


def _dist(a, b):
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


# ===== 手勢關節編號 =====
WRIST = 0
THUMB_MCP, THUMB_IP, THUMB_TIP = 2, 3, 4
MIDDLE_MCP = 9
# (指尖, PIP 關節)用來判斷食指/中指/無名指/小指是否伸直
FINGER_TIP_PIP = ((8, 6), (12, 10), (16, 14), (20, 18))

# 如果比 5 的時候大拇指沒被算到(或比 4 卻多算成 5),代表大拇指左右判斷跟你的
# 鏡頭方向相反,把這個常數改成 True 試試看。
MIRROR_THUMB_TEST = False


def is_thumb_extended(points, handedness_label):
    tip_x = points[THUMB_TIP][0]
    ip_x = points[THUMB_IP][0]
    is_right_hand = (handedness_label == 'Right') != MIRROR_THUMB_TEST
    return (tip_x < ip_x) if is_right_hand else (tip_x > ip_x)


def count_extended_fingers(points, handedness_label):
    wrist = points[WRIST]
    count = sum(1 for tip, pip in FINGER_TIP_PIP if _dist(points[tip], wrist) > _dist(points[pip], wrist) * 1.15)
    if is_thumb_extended(points, handedness_label):
        count += 1
    return count


def palm_size(points):
    return _dist(points[WRIST], points[MIDDLE_MCP])


def hand_orientation_angle(points):
    # 手腕(0)指向中指根部(9)的方向,拿來偵測「轉手」的手勢,驅動物件自轉
    wx, wy = points[WRIST]
    mx, my = points[MIDDLE_MCP]
    return np.arctan2(my - wy, mx - wx)


# ===== 粒子造型的幾何產生器(座標都是物件自己的局部座標,中心在原點)=====

def _gen_sphere(n, radius, shell_lo=0.80, shell_pow=2, b_lo=0.55, b_hi=1.0, hemisphere=False, y_shift=0.0):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        u, v = random.random(), random.random()
        theta = 2 * np.pi * u
        phi = np.arccos((1 - v) if hemisphere else (2 * v - 1))
        r = radius * (shell_lo + (1 - shell_lo) * random.random() ** shell_pow)
        x = r * np.sin(phi) * np.cos(theta)
        z = r * np.sin(phi) * np.sin(theta)
        y = y_shift + r * np.cos(phi)
        pts[i] = (x, y, z, random.uniform(b_lo, b_hi))
    return pts


def _gen_ring(n, base_radius, r_lo_mult, r_hi_mult, tilt=0.35, thickness=0.02, y_center=0.0, b_lo=0.6, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    cos_t, sin_t = np.cos(tilt), np.sin(tilt)
    for i in range(n):
        r = base_radius * random.uniform(r_lo_mult, r_hi_mult)
        theta = random.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        z = r * np.sin(theta)
        y = random.uniform(-1, 1) * base_radius * thickness
        y, z = y * cos_t - z * sin_t, y * sin_t + z * cos_t
        pts[i] = (x, y_center + y, z, random.uniform(b_lo, b_hi))
    return pts


def _gen_cone_surface(n, y_top, y_bottom, r_top, r_bottom, b_lo=0.6, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        t = random.random()
        r = r_top + (r_bottom - r_top) * t
        theta = random.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        z = r * np.sin(theta)
        y = y_top + (y_bottom - y_top) * t
        pts[i] = (x, y, z, random.uniform(b_lo, b_hi))
    return pts


def _gen_segments(n, segments, b_lo=0.8, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    m = len(segments)
    for i in range(n):
        p0, p1 = segments[random.randrange(m)]
        t = random.random()
        pts[i] = (p0[0] + (p1[0] - p0[0]) * t,
                  p0[1] + (p1[1] - p0[1]) * t,
                  p0[2] + (p1[2] - p0[2]) * t,
                  random.uniform(b_lo, b_hi))
    return pts


def _gen_patch(n, radius, theta0, phi0, half_extent, b_lo=0.6, b_hi=0.9):
    # 在球面(theta0, phi0)附近取一小塊方形色斑(用切平面近似投影,做出星球表面的色塊細節)
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        du = random.uniform(-half_extent, half_extent)
        dv = random.uniform(-half_extent, half_extent)
        theta = theta0 + du / max(np.sin(phi0), 0.35)
        phi = phi0 + dv
        r = radius * 1.012
        x = r * np.sin(phi) * np.cos(theta)
        z = r * np.sin(phi) * np.sin(theta)
        y = r * np.cos(phi)
        pts[i] = (x, y, z, random.uniform(b_lo, b_hi))
    return pts


def _heart_ok(u, v):
    return (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0


def _gen_heart_patch(n, radius, theta0=0.0, phi0=np.pi / 2, patch_scale=0.5, b_lo=0.85, b_hi=1.0):
    # 在球面上貼一塊愛心形狀的亮色斑(冥王星表面著名的湯博region 心形亮斑)
    pts = np.empty((n, 4), dtype='float64')
    got = 0
    attempts = 0
    while got < n and attempts < n * 40:
        attempts += 1
        u = random.uniform(-1.3, 1.3)
        v = random.uniform(-1.15, 1.35)
        if not _heart_ok(u, -v):   # 翻轉 v,讓愛心尖端朝下,符合一般視覺習慣
            continue
        theta = theta0 + u * patch_scale / max(np.sin(phi0), 0.35)
        phi = phi0 + v * patch_scale
        r = radius * 1.015
        x = r * np.sin(phi) * np.cos(theta)
        z = r * np.sin(phi) * np.sin(theta)
        y = r * np.cos(phi)
        pts[got] = (x, y, z, random.uniform(b_lo, b_hi))
        got += 1
    return pts[:got]


# ---------- 1. 羽球(cork 半球 + 羽毛裙擺錐)----------
CORK_R = 26.0
BADMINTON_CORK = _gen_sphere(260, CORK_R, shell_lo=0.85, shell_pow=1, b_lo=0.75, b_hi=1.0,
                              hemisphere=True, y_shift=55.0)

SKIRT_RIBS = 16
SKIRT_RIB_JITTER = 0.10


def _gen_skirt(n, y_top, y_bottom, r_top, r_bottom, b_lo=0.7, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        rib = random.randrange(SKIRT_RIBS)
        theta = rib * (2 * np.pi / SKIRT_RIBS) + random.uniform(-SKIRT_RIB_JITTER, SKIRT_RIB_JITTER)
        t = random.random()
        r = (r_top + (r_bottom - r_top) * t) * random.uniform(0.94, 1.06)   # 輕微膨鬆感,像真的羽毛裙擺
        y = y_top + (y_bottom - y_top) * t
        pts[i] = (r * np.cos(theta), y, r * np.sin(theta), random.uniform(b_lo, b_hi))
    return pts


BADMINTON_SKIRT = _gen_skirt(1000, y_top=50.0, y_bottom=-85.0, r_top=22.0, r_bottom=100.0)
CORK_COLOR = (210, 235, 250)      # BGR,米白色軟木頭
FEATHER_COLOR = (250, 250, 250)   # BGR,白色羽毛

# ---------- 2. 海王星(藍色星球 + 暗斑 + 淡淡光環)----------
NEPTUNE_R = 100.0
NEPTUNE_SPHERE = _gen_sphere(1500, NEPTUNE_R, shell_lo=0.82, shell_pow=2, b_lo=0.55, b_hi=1.0)
NEPTUNE_SPOT = _gen_patch(120, NEPTUNE_R, theta0=0.9, phi0=1.3, half_extent=0.22, b_lo=0.35, b_hi=0.55)
NEPTUNE_RING = _gen_ring(500, NEPTUNE_R, 1.5, 1.62, tilt=0.4, thickness=0.01, b_lo=0.35, b_hi=0.6)
NEPTUNE_COLOR = (230, 110, 60)     # BGR,海王星的靛藍色
NEPTUNE_SPOT_COLOR = (150, 60, 30)     # BGR,大暗斑(深藍)
NEPTUNE_RING_COLOR = (235, 210, 190)   # BGR,淡淡的白藍色光環

# ---------- 3. 冥王星(灰棕色星球 + 心形亮斑)----------
PLUTO_R = 68.0
PLUTO_SPHERE = _gen_sphere(1100, PLUTO_R, shell_lo=0.82, shell_pow=2, b_lo=0.55, b_hi=0.95)
PLUTO_HEART = _gen_heart_patch(220, PLUTO_R, theta0=0.0, phi0=np.pi / 2, patch_scale=0.55)
PLUTO_COLOR = (150, 175, 205)      # BGR,灰棕色岩石表面
PLUTO_HEART_COLOR = (215, 230, 250)   # BGR,湯博區域的亮白色

# ---------- 4. 鑽石(冠部錐 + 亭部錐 + 腰圍)----------
DIAMOND_GIRDLE_R = 72.0
DIAMOND_CROWN = _gen_cone_surface(650, y_top=95.0, y_bottom=15.0, r_top=6.0, r_bottom=DIAMOND_GIRDLE_R)
DIAMOND_PAVILION = _gen_cone_surface(750, y_top=15.0, y_bottom=-125.0, r_top=DIAMOND_GIRDLE_R, r_bottom=0.0)
DIAMOND_GIRDLE = _gen_ring(260, DIAMOND_GIRDLE_R, 0.985, 1.015, tilt=0.0, thickness=0.01, y_center=15.0,
                            b_lo=0.85, b_hi=1.0)
DIAMOND_COLOR = (255, 250, 225)   # BGR,冰藍白色
DIAMOND_GIRDLE_COLOR = (255, 255, 255)

# ---------- 5. 寶箱(木箱本體 + 半圓筒箱蓋 + 金色鑲邊 + 鎖扣)----------
CHEST_HALF_W, CHEST_HALF_D = 78.0, 52.0
CHEST_Y_BOTTOM, CHEST_Y_TOP = -88.0, 8.0
CHEST_MID_Y = (CHEST_Y_BOTTOM + CHEST_Y_TOP) / 2


def _gen_box_faces(n, half_w, half_d, y_bottom, y_top, b_lo=0.5, b_hi=0.9):
    pts = np.empty((n, 4), dtype='float64')
    faces = ('front', 'back', 'left', 'right', 'bottom')
    for i in range(n):
        f = faces[random.randrange(len(faces))]
        if f in ('front', 'back'):
            x, y = random.uniform(-half_w, half_w), random.uniform(y_bottom, y_top)
            z = half_d if f == 'front' else -half_d
        elif f in ('left', 'right'):
            z, y = random.uniform(-half_d, half_d), random.uniform(y_bottom, y_top)
            x = -half_w if f == 'left' else half_w
        else:
            x, z, y = random.uniform(-half_w, half_w), random.uniform(-half_d, half_d), y_bottom
        pts[i] = (x, y, z, random.uniform(b_lo, b_hi))
    return pts


def _gen_lid(n, radius, half_d, y_base, b_lo=0.5, b_hi=0.9):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        ang = random.uniform(0, np.pi)   # 只取上半圓(0~pi 讓 sin >= 0),做出拱形箱蓋
        z = random.uniform(-half_d, half_d)
        pts[i] = (radius * np.cos(ang), y_base + radius * np.sin(ang), z, random.uniform(b_lo, b_hi))
    return pts


def _gen_lid_rim(n, radius, half_d, y_base, b_lo=0.85, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        ang = random.uniform(0, np.pi)
        z = half_d if random.random() < 0.5 else -half_d
        pts[i] = (radius * np.cos(ang), y_base + radius * np.sin(ang), z, random.uniform(b_lo, b_hi))
    return pts


CHEST_BODY = _gen_box_faces(900, CHEST_HALF_W, CHEST_HALF_D, CHEST_Y_BOTTOM, CHEST_Y_TOP)
CHEST_LID = _gen_lid(500, CHEST_HALF_W, CHEST_HALF_D, CHEST_Y_TOP)
CHEST_LID_RIM = _gen_lid_rim(160, CHEST_HALF_W, CHEST_HALF_D, CHEST_Y_TOP)

_CHEST_EDGES = [
    # 4 條垂直邊
    ((-CHEST_HALF_W, CHEST_Y_BOTTOM, -CHEST_HALF_D), (-CHEST_HALF_W, CHEST_Y_TOP, -CHEST_HALF_D)),
    ((CHEST_HALF_W, CHEST_Y_BOTTOM, -CHEST_HALF_D), (CHEST_HALF_W, CHEST_Y_TOP, -CHEST_HALF_D)),
    ((-CHEST_HALF_W, CHEST_Y_BOTTOM, CHEST_HALF_D), (-CHEST_HALF_W, CHEST_Y_TOP, CHEST_HALF_D)),
    ((CHEST_HALF_W, CHEST_Y_BOTTOM, CHEST_HALF_D), (CHEST_HALF_W, CHEST_Y_TOP, CHEST_HALF_D)),
]
for _y in (CHEST_Y_BOTTOM, CHEST_Y_TOP, CHEST_MID_Y):
    _CHEST_EDGES += [
        ((-CHEST_HALF_W, _y, -CHEST_HALF_D), (CHEST_HALF_W, _y, -CHEST_HALF_D)),
        ((CHEST_HALF_W, _y, -CHEST_HALF_D), (CHEST_HALF_W, _y, CHEST_HALF_D)),
        ((CHEST_HALF_W, _y, CHEST_HALF_D), (-CHEST_HALF_W, _y, CHEST_HALF_D)),
        ((-CHEST_HALF_W, _y, CHEST_HALF_D), (-CHEST_HALF_W, _y, -CHEST_HALF_D)),
    ]
CHEST_TRIM = _gen_segments(700, _CHEST_EDGES)


def _gen_lock(n, mid_y, half_d, w=18.0, h=24.0, b_lo=0.85, b_hi=1.0):
    pts = np.empty((n, 4), dtype='float64')
    for i in range(n):
        pts[i] = (random.uniform(-w / 2, w / 2), mid_y + random.uniform(-h / 2, h / 2), half_d + 0.8,
                  random.uniform(b_lo, b_hi))
    return pts


CHEST_LOCK = _gen_lock(80, CHEST_MID_Y, CHEST_HALF_D)

WOOD_COLOR = (35, 85, 130)     # BGR,深木紋棕色
GOLD_COLOR = (20, 190, 240)    # BGR,金色鑲邊
LOCK_COLOR = (10, 140, 205)    # BGR,鎖扣用比鑲邊深一點的古銅金

# ---------- 尚未比出有效手勢時的預設造型(淡灰色球體提示)----------
IDLE_SPHERE = _gen_sphere(320, 55.0, shell_lo=0.9, shell_pow=1, b_lo=0.4, b_hi=0.75)
IDLE_COLOR = (190, 190, 190)

SHAPES = {
    1: [(BADMINTON_CORK, CORK_COLOR), (BADMINTON_SKIRT, FEATHER_COLOR)],
    2: [(NEPTUNE_SPHERE, NEPTUNE_COLOR), (NEPTUNE_SPOT, NEPTUNE_SPOT_COLOR), (NEPTUNE_RING, NEPTUNE_RING_COLOR)],
    3: [(PLUTO_SPHERE, PLUTO_COLOR), (PLUTO_HEART, PLUTO_HEART_COLOR)],
    4: [(DIAMOND_CROWN, DIAMOND_COLOR), (DIAMOND_PAVILION, DIAMOND_COLOR), (DIAMOND_GIRDLE, DIAMOND_GIRDLE_COLOR)],
    5: [(CHEST_BODY, WOOD_COLOR), (CHEST_LID, WOOD_COLOR), (CHEST_TRIM, GOLD_COLOR),
        (CHEST_LID_RIM, GOLD_COLOR), (CHEST_LOCK, LOCK_COLOR)],
}
SHAPE_NAMES = {0: '請比出 1~5 手指', 1: '羽球', 2: '海王星', 3: '冥王星', 4: '鑽石', 5: '寶箱'}
IDLE_SHAPE = [(IDLE_SPHERE, IDLE_COLOR)]

# ===== 攝影機/物件狀態(由手勢驅動)=====
camera_azimuth = 0.0
camera_distance = 560.0
prev_hand_angle = None
current_shape = 0
stable_count = -1
count_hold_frames = 0


def update_state(hands):
    global camera_azimuth, camera_distance, prev_hand_angle, current_shape, stable_count, count_hold_frames
    if not hands:
        camera_azimuth += IDLE_ROTATE_SPEED   # 沒有手的時候讓造型緩慢自轉,畫面不會呆掉
        prev_hand_angle = None
        stable_count = -1
        count_hold_frames = 0
        return None

    points, label = hands[0]   # 只用偵測到的第一隻手

    # 轉手 → 物件自轉角度
    angle = hand_orientation_angle(points)
    if prev_hand_angle is not None:
        delta = angle - prev_hand_angle
        delta = (delta + np.pi) % (2 * np.pi) - np.pi   # 修正繞過 -pi/pi 邊界的跳動
        camera_azimuth += delta
    prev_hand_angle = angle

    # 手掌貼近/遠離鏡頭 → 縮放(用手腕到中指根部的像素距離當作深度的替代指標)
    size = palm_size(points)
    t = np.clip((size - PALM_SIZE_FAR) / (PALM_SIZE_NEAR - PALM_SIZE_FAR), 0.0, 1.0)
    target_distance = MAX_CAMERA_DISTANCE - t * (MAX_CAMERA_DISTANCE - MIN_CAMERA_DISTANCE)
    camera_distance += (target_distance - camera_distance) * ZOOM_SMOOTH

    # 手指數 → 切換造型(需要連續穩定 GESTURE_HOLD_FRAMES 幀才切換,避免手指過渡時的誤判閃爍)
    n = count_extended_fingers(points, label)
    if n == stable_count:
        count_hold_frames += 1
    else:
        stable_count = n
        count_hold_frames = 1
    if 1 <= n <= 5 and count_hold_frames >= GESTURE_HOLD_FRAMES:
        current_shape = n
    return n


def project_points(points_3d):
    cos_a, sin_a = np.cos(camera_azimuth), np.sin(camera_azimuth)
    x, y, z = points_3d[:, 0], points_3d[:, 1], points_3d[:, 2]
    xr = x * cos_a - z * sin_a       # 繞 Y 軸自轉
    zr = x * sin_a + z * cos_a
    depth = np.clip(zr + camera_distance, 1e-3, None)
    scale = FOCAL_LENGTH / depth
    return xr * scale, y * scale, zr, scale


def sparkle_bright(points4d, chance=0.06, boost=(1.3, 1.9)):
    # 鑽石用的閃爍效果:每一幀隨機挑一小部分粒子加亮,模擬鑽石反光閃爍
    bright = points4d[:, 3].copy()
    mask = np.random.random(len(bright)) < chance
    if mask.any():
        bright[mask] = np.random.uniform(boost[0], boost[1], int(mask.sum()))
    return bright


def draw_point_cloud(canvas, points_4d, base_color, bright_override=None):
    w, h = canvas.shape[1], canvas.shape[0]
    sx, sy, zr, scale = project_points(points_4d[:, :3])
    brightness = points_4d[:, 3] if bright_override is None else bright_override
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
                       (min(255, int(b * fade)), min(255, int(g * fade)), min(255, int(r * fade))), -1)


def render_scene(camera_frame, detection_result):
    height, width = camera_frame.shape[:2]
    canvas = np.zeros((height, width, 3), dtype='uint8')

    hands = [
        ([(lm.x * width, lm.y * height) for lm in hand_landmarks],
         handedness[0].category_name if handedness else 'Right')
        for hand_landmarks, handedness in zip(detection_result.hand_landmarks, detection_result.handedness)
    ]
    n = update_state(hands)
    shape_group = SHAPES.get(current_shape, IDLE_SHAPE)

    glow = np.zeros_like(canvas)
    for pts, color in shape_group:
        bright = sparkle_bright(pts) if current_shape == 4 else None
        draw_point_cloud(glow, pts, color, bright)
    glow = cv2.GaussianBlur(glow, (9, 9), 0)
    canvas = cv2.add(canvas, glow)
    for pts, color in shape_group:
        bright = sparkle_bright(pts) if current_shape == 4 else None
        draw_point_cloud(canvas, pts, color, bright)

    gesture_text = f"{n} 指" if n is not None else '未偵測到手'
    cv2.putText(canvas, f"手勢: {gesture_text}   造型: {SHAPE_NAMES.get(current_shape, SHAPE_NAMES[0])}   "
                         f"距離: {camera_distance:.0f}",
                (14, 28), cv2.FONT_HERSHEY_DUPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
    cv2.putText(canvas, "1=羽球 2=海王星 3=冥王星 4=鑽石 5=寶箱",
                (14, 54), cv2.FONT_HERSHEY_DUPLEX, 0.5, (150, 150, 150), 1, cv2.LINE_AA)

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

        annotated = render_scene(frame, hand_landmarker_result)
        cv2.imshow('3D particle gesture', annotated)
        if cv2.waitKey(5) in (ord('q'), ord('Q')):
            break
cap.release()
cv2.destroyAllWindows()
