# 08 _ yolo webcam 推論 + browser 串流 (MJPEG)
# 為什麼要這樣:
# - opencv-python-headless 沒 GUI，cv2.imshow 打不開視窗
# - 走 browser 不用 GUI opencv，還能讓我們在同 WiFi 看模型跑
# 
# 起服務:
#   python 08_webcam串流推論.py
# browser: http://localhost:9001/
# same (WiFi): http:://192.168.1.1xx:9001/

import io
import time
import threading
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response, render_template_string
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent

# --- find the newest best.py (same logic with 07) ---
search_dirs = [BASE / "runs", BASE.parent.parent / "runs"]
weights_candidates = []
for d in search_dirs:
    if d.exists():
        weights_candidates.extend(d.rglob("best.pt"))
weights_candidates = sorted(weights_candidates, key=lambda p: p.stat().st_time, reverse=True)
if not weights_candidates:
    raise FileNotFoundError("Can't found best.pt, run 05_訓練自己的YOLO.py")
MODEL_PATH = weights_candidates[0]
print(f"load the newest model: {MODEL_PATH}")
if len(weights_candidates) > 1:
    print(f"found in total {len(weights_candidates)} best.pt, use the newest")

model = YOLO(str(MODEL_PATH))
print(f"types: {model.names}")

# --- chinese font ---

import os
FONT_CANDIDATES = [
    "C:/Windows/Fonts/msjg.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)

def 依類別配色(name):
    h = hash(name) & 0xFFFFFF
    return (h & 0xFF, (h >> 8) & 0xFF, (h >> 16) & 0xFF)

def 畫中文label(img_bgr, text, xy, size, bg_bgr):
    img_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(FONT_PATH, size)
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    x, y = xy
    bg_rgb = (bg_bgr[2], bg_bgr[1], bg_bgr[0])
    draw.rectangle((x, y , x + tw + 6, y + th + 6), fill=bg_rgb)
    draw.text((x + 3,  y + 3), text, font=font, fill=(255, 255, 255))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

# --- camera + 推論執行緒 ---
# a thread 負責 read frame + 推論，把 newest frame to save
# Flask per client take newest for frame to push
newest_frame = [None]
running = [True]
fps_hist = []

def grab_loop():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("無法開啟 webcam")
        running[0] = False
        return

    while running[0]:
        t0 = time.time()
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        # YOLO 推論
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
                color = 依類別配色(name)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 3)
                frame = 畫中文label(frame, f"{name} {conf*100:.0f}%",
                                  (int(x1), max(0, int(y1) - 30)), 20, color)

        # FPS
        fps_hist.append(1.0 / max(time.time() - t0, 1e-3))
        if len(fps_hist) > 30:
            fps_hist.pop(0)
        fps = sum(fps_hist) / len(fps_hist)
        frame = 畫中文label(frame, f"FPS {fps:.1f}  |  {MODEL_PATH.parent.parent.name}",
                          (10, 10), 22, (30, 30, 30))

        # JPEG 編碼並更新最新 frame
        ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            newest_frame[0] = jpg.tobytes()

    cap.release()
    print("webcam thread 結束")


threading.Thread(target=grab_loop, daemon=True).start()

# ====== Flask 串流 ======
app = Flask(__name__)

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>YOLO 自訓練 - Fe 偵測</title>
<style>
  body { margin:0; background:#111; color:#eee; font-family:'Microsoft JhengHei',sans-serif;
         display:flex; flex-direction:column; align-items:center; padding:20px; }
  h1 { margin-bottom:16px; }
  img { max-width:100%; border:2px solid #444; border-radius:8px; }
  .hint { color:#888; margin-top:12px; font-size:14px; }
</style>
</head>
<body>
  <h1>YOLO 自訓練模型 — Fe 即時偵測</h1>
  <img src="/stream">
  <div class="hint">Server 抓 webcam + 跑模型，畫面即時串流到瀏覽器</div>
</body>
</html>"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

def mjpeg_generator():
    while True:
        f = newest_frame[0]
        if f is None:
            time.sleep(0.1)
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n"
               b"Content-Length: " + str(len(f)).encode() + b"\r\n\r\n" +
               f + b"\r\n")

@app.route("/stream")
def stream():
    return Response(mjpeg_generator(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


if __name__ == "__main__":
    print("=" * 50)
    print("YOLO webcam 串流服務")
    print("=" * 50)
    print("本機打:      http://localhost:9091/")
    print("學員同 WiFi: http://192.168.1.102:9091/")
    print("按 Ctrl+C 停止")
    print("=" * 50)
    try:
        app.run(host="0.0.0.0", port=9091, threaded=True)
    finally:
        running[0] = False