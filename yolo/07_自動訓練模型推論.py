# 07 - 用剛剛訓練好的 yolo 模型做 webcam 即時推論
# 前置: 跑過 05_訓練好的 yolo.py 會產生 runs/train/weights/best.py
# 這支腳本自動找最新版的 run 的 best.py

import os
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent

# --- find the newest of best.pt ---
# 05. now will be find the abouslte location to save to yol/runs/; for can adapt run project root version, also will scan there.
search_dirs = [BASE / "runs", BASE.parent.parent / "runs"]
weights_candidates = []
for d in search_dirs:
    if d.exists():
        weights_candidates.extend(d.rglob("best.pt"))
weights_candidates = sorted(weights_candidates, key=lambda p: p.stat().st_mtime, reverse=True)
if not weights_candidates:
    raise FileNotFoundError(
        "can't find best.pt. need to run 05_訓練自己的yolo.py finished tranning"
    )
MODEL_PATH = weights_candidates[0]
print(f"load the newest model:{MODEL_PATH}")
if len(weights_candidates) > 1:
    print(f"find total: {len(weights_candidates)} best.pt, use newest")

model = YOLO(str(MODEL_PATH))
print(f"types name:{model.names}")

# chinese font(if use chinese when use self tranning)
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjh.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    print("警告: 找不到中文字型,文字會用預設英文字體畫(中文字可能變成問號)")

def according_types_to_match_color(name):
    h = hash(name) & 0xFFFFFF
    return (h & 0xFF, (h >> 8) & 0xFF, (h >> 16) & 0xFF)

def 畫中文label(img_bgr, text, xy, size, bg_bgr):
    if FONT_PATH is None:
        x, y = xy
        cv2.rectangle(img_bgr, (x, y), (x + 8 * len(text) + 6, y + size + 6), bg_bgr, -1)
        cv2.putText(img_bgr, text, (x + 3, y + size), cv2.FONT_HERSHEY_SIMPLEX,
                    size / 30, (255, 255, 255), 2)
        return img_bgr
    img_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(FONT_PATH, size)
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    x, y = xy
    bg_bgr = (bg_bgr[2], bg_bgr[1], bg_bgr[0])
    draw.rectangle((x, y, x + tw + 6, y + th + 6), fill=bg_bgr)
    draw.text((x + 3, y + 3), text, font=font, fill=(255, 255, 255))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# ---open webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("can't open webcam")

print("click q to exit; press s to save picture to snapshot.png")

fps_hist = []

while True:
    ret, frame = cap.read()
    if not ret:
        break
    t0 = time.time()

    results = model.predict(frame, imgsz=640, conf=0.4, verbose=False)

    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes.xyxy[i].tolist()
            conf = float(boxes.conf[i])
            cls_id = int(boxes.cls[i])
            name = model.names[cls_id]
            color = according_types_to_match_color(name)
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
            frame = 畫中文label(frame, f"{name} {conf*100:.0f}%",
                               (int(x1), max(0, int(y1) - 30)), 20, color)
    fps_hist.append(1.0 / max(time.time() - t0, 1e-3))
    if len(fps_hist) > 30:
        fps_hist.pop(0)
    fps = sum(fps_hist) / len(fps_hist)
    frame = 畫中文label(frame, f"FPS {fps:.1f} | {MODEL_PATH.parent.parent.name}",
                       (10, 10), 22, (30, 30, 30))

    cv2.imshow("YOLO 自動推論", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    if key == ord("s"):
        cv2.imwrite("snapshot.png", frame)
        print("已存 snapshot.png")

cap.release()
cv2.destroyAllWindows()