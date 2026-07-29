import cv2
import numpy as np

# ---- 電阻色碼表 ----
DIGIT = {
    'black': 0, 'brown': 1, 'red': 2, 'orange': 3, 'yellow': 4,
    'green': 5, 'blue': 6, 'violet': 7, 'grey': 8, 'white': 9,
}
MULTIPLIER = {
    'black': 1, 'brown': 10, 'red': 100, 'orange': 1000, 'yellow': 10000,
    'green': 100000, 'blue': 1000000, 'violet': 10000000, 'grey': 100000000,
    'white': 1000000000, 'gold': 0.1, 'silver': 0.01,
}
TOLERANCE = {
    'brown': 1, 'red': 2, 'green': 0.5, 'blue': 0.25, 'violet': 0.1,
    'grey': 0.05, 'gold': 5, 'silver': 10,
}

BAND_COLORS = {  # 畫框用的顯示色 (BGR)
    'black': (0, 0, 0), 'brown': (19, 69, 139), 'red': (0, 0, 255),
    'orange': (0, 140, 255), 'yellow': (0, 255, 255), 'green': (0, 255, 0),
    'blue': (255, 0, 0), 'violet': (211, 0, 148), 'grey': (128, 128, 128),
    'white': (255, 255, 255), 'gold': (0, 215, 255), 'silver': (192, 192, 192),
}


def classify_color(h, s, v):
    # 可調參數：依現場燈光/鏡頭微調下面的門檻
    # white/silver 門檻拉高、拉嚴，避免圓柱電阻表面反光被誤判成色環
    if v < 50:
        return 'black'
    if s < 30 and v > 220:
        return 'white'
    if s < 60:
        return 'silver' if v > 215 else 'grey'
    if h < 8 or h >= 170:
        return 'red'
    if 8 <= h < 18:
        return 'orange' if v > 150 else 'brown'
    if 18 <= h < 22:
        return 'gold' if s < 180 else 'orange'
    if 22 <= h < 33:
        return 'yellow'
    if 33 <= h < 85:
        return 'green'
    if 85 <= h < 135:
        return 'blue'
    if 135 <= h < 170:
        return 'violet'
    return 'unknown'


def _hsv_dist(a, b):
    dh = min(abs(a[0] - b[0]), 180 - abs(a[0] - b[0]))
    return (dh * 2) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def analyze_roi(roi):
    h, w = roi.shape[:2]
    blur = cv2.GaussianBlur(roi, (3, 3), 0)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV).astype(float)

    # 取水平中段一條較寬的帶，逐欄取「中位數」而非平均數，避免圓柱表面反光的亮點拉歪顏色判斷
    strip = hsv[int(h * 0.25):int(h * 0.75), :]
    col_hsv = np.median(strip, axis=0)  # shape (w, 3)

    # 用「左邊一小段平均」vs「右邊一小段平均」比較邊界，比只比較緊鄰兩欄更耐得住模糊/漸層邊界
    half = max(2, w // 60)
    diff_threshold = 30 ** 2  # 可調參數：數值越小分段越敏感

    def window_dist(x):
        l0, l1 = max(0, x - half), x
        r0, r1 = x, min(w, x + half)
        if l1 <= l0 or r1 <= r0:
            return 0
        left = col_hsv[l0:l1].mean(axis=0)
        right = col_hsv[r0:r1].mean(axis=0)
        return _hsv_dist(left, right)

    segments = []
    seg_start = 0
    for x in range(1, w + 1):
        if x == w or window_dist(x) > diff_threshold:
            seg_hsv = col_hsv[seg_start:x].mean(axis=0)
            segments.append({
                'x1': seg_start, 'x2': x, 'width': x - seg_start,
                'hsv': seg_hsv, 'color': classify_color(*seg_hsv),
            })
            seg_start = x

    # 色環一定比本體/背景窄很多，用寬度濾掉本體，而不是用顏色名稱猜
    min_w = max(3, int(w * 0.015))
    max_w = int(w * 0.30)
    body_w = int(w * 0.12)

    bands = [
        {'color': seg['color'], 'x1': seg['x1'], 'x2': seg['x2']}
        for seg in segments
        if seg['color'] != 'unknown' and min_w <= seg['width'] <= min(max_w, body_w - 1)
    ]
    return segments, bands


def decode_resistance(bands):
    colors = [b['color'] for b in bands]
    n = len(colors)
    if n < 4:
        return None  # 至少要抓到 4 環 (2位數字+倍率+誤差) 才能穩定判讀

    # 金/銀只會是誤差環，且顏色不會跟數字/倍率色撞色，拿來定位最可靠
    tol_idx = None
    if colors[-1] in ('gold', 'silver'):
        tol_idx = n - 1
    elif colors[0] in ('gold', 'silver'):
        colors = colors[::-1]
        tol_idx = n - 1

    if tol_idx is not None:
        rest = colors[:tol_idx]
        if len(rest) < 3:
            return None
        # 只取最靠近誤差環的 2 環數字 + 1 環倍率，前面多出來的雜訊(如反光)自動忽略
        digits, mult_color = rest[-3:-1], rest[-1]
        tol_color = colors[tol_idx]
    elif n >= 5:
        digits, mult_color, tol_color = colors[0:3], colors[3], colors[4]
    else:
        return None  # 沒有金/銀誤差環又不到 5 環，資訊不足無法判讀

    if mult_color not in MULTIPLIER or any(d not in DIGIT for d in digits):
        return None

    digit_value = 0
    for d in digits:
        digit_value = digit_value * 10 + DIGIT[d]

    ohms = digit_value * MULTIPLIER[mult_color]
    tolerance = TOLERANCE.get(tol_color, 20)
    return ohms, tolerance


def format_resistance(ohms):
    if ohms >= 1_000_000:
        return f"{ohms / 1_000_000:.2f} M ohm"
    if ohms >= 1_000:
        return f"{ohms / 1_000:.2f} k ohm"
    return f"{ohms:.2f} ohm"


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Can't open camera")
    exit()

tracker = None  # 用 MIL 追蹤器讓框跟著電阻走，不用固定死座標 (跟 opencv 多物件追蹤.py 同一套)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
        break

    frame = cv2.resize(frame, (960, 540))
    keyName = cv2.waitKey(1)

    if keyName == ord('q'):
        break
    if keyName == ord('a'):
        box = cv2.selectROI('resistor', frame, showCrosshair=False, fromCenter=False)
        if box[2] > 0 and box[3] > 0:
            tracker = cv2.TrackerMIL.create()
            tracker.init(frame, box)
        else:
            tracker = None

    tracked = False
    if tracker is not None:
        tracked, box = tracker.update(frame)

    if tracked:
        x, y, w, h = (int(v) for v in box)
        roi = frame[y:y + h, x:x + w]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        segments, bands = analyze_roi(roi)
        for b in bands:
            color = BAND_COLORS.get(b['color'], (255, 255, 255))
            cv2.rectangle(frame, (x + b['x1'], y), (x + b['x2'], y + h), color, 2)

        result = decode_resistance(bands)
        if result:
            ohms, tolerance = result
            text = f"{format_resistance(ohms)}  +-{tolerance}%"
            text_color = (0, 255, 0)
        else:
            found = ",".join(b['color'] for b in bands) or "none"
            text = f"segments={len(segments)} bands={len(bands)}: {found}"
            text_color = (0, 255, 255)
        cv2.putText(frame, text, (x, max(20, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
    else:
        tracker = None
        cv2.putText(frame, "press 'a' to select resistor, 'q' to quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow('resistor', frame)

cap.release()
cv2.destroyAllWindows()
