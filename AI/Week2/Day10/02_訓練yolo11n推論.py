# yolo11n 訓練模型即時 webcam 偵測
# install pip install ultralytics opencv-python pillow

import os
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont

# 載入模型

model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)
print(f"模型類別數: {len(model.names)}")

# 中文字形
FONT_CANDIDATES = [
    "C:/windows/fonts/msjh.ttc",  # 微軟正黑體
    "C:/windows/fonts/msjhbd.ttc",  # 微軟正黑體粗體
    "C:/Windows/Fonts/simhei.ttf",  # 微軟雅黑體
]
font_path = next((Path(f) for f in FONT_CANDIDATES if Path(f).exists()), None)

coco_zh = {
    "person": "人", "bicycle": "腳踏車", "car": "汽車", "motorcycle": "摩托車", "airplane": "飛機", "bus": "公車", "train": "火車",
    "truck": "卡車", "boat": "船", "traffic light": "交通燈", "fire hydrant": "消防栓", "stop sign": "停車標誌", "parking meter": "停車計時器", "bench": "長椅", "bird": "鳥",
    "cat": "貓", "dog": "狗", "horse": "馬", "sheep": "羊", "cow": "牛", "elephant": "大象", "bear": "熊", "zebra": "斑馬", "giraffe": "長頸鹿", "backpack": "背包",
    "umbrella": "雨傘", "handbag": "手提包", "tie": "領帶", "suitcase": "行李箱", "frisbee": "飛盤", "skis": "滑雪板", "snowboard": "滑雪板", "sports ball": "運動球",
    "kite": "風箏", "baseball bat": "棒球棒", "baseball glove": "棒球手套", "skateboard": "滑板", "surfboard": "衝浪板", "tennis racket": "網球拍", "bottle": "瓶子", "wine glass": "酒杯", "cup": "杯子",
    "fork": "叉子", "knife": "刀子", "spoon": "湯匙", "bowl": "碗", "banana": "香蕉", "apple": "蘋果", "sandwich": "三明治", "orange": "柳橙", "broccoli": "花椰菜", "carrot": "胡蘿蔔",
    "hot dog": "熱狗", "pizza": "披薩", "donut": "甜甜圈", "cake": "蛋糕", "chair": "椅子", "couch": "沙發", "potted plant": "盆栽植物", "bed": "床", "dining table": "餐桌",
    "toilet": "馬桶", "tv": "電視", "laptop": "筆記型電腦", "mouse": "滑鼠", "remote": "遙控器", "keyboard": "鍵盤", "cell phone": "手機", "microwave": "微波爐", "oven": "烤箱",
    "toaster": "烤麵包機", "sink": "水槽", "refrigerator": "冰箱", "book": "書", "clock": "時鐘", "vase": "花瓶", "scissors": "剪刀", "teddy bear": "泰迪熊", "hair drier": "吹風機",
    "toothbrush": "牙刷", "hair brush": "梳子", "hair dryer": "吹風機", "tooth paste": "牙膏", "tooth brush": "牙刷", "toilet paper": "衛生紙", "soap": "肥皂", "shampoo": "洗髮精", "conditioner": "護髮素", "lotion": "乳液", "perfume": "香水", "deodorant": "除臭劑", "razor": "刮鬍刀", "towel": "毛巾",
    "hair": "頭髮", "face": "臉", "eye": "眼睛", "ear": "耳朵", "nose": "鼻子", "mouth": "嘴巴", "tooth": "牙齒", "tongue": "舌頭", "neck": "脖子", "shoulder": "肩膀",
}

def 依類別配色(name):
    h = hash(name) & 0xffffff
    return (h & 0xff, (h >> 8) & 0xff, (h >> 16) & 0xff)

def 劃中文標籤(img_bgr, text, xy, size, bg_bgr):
    """在指定位置話「彩色底+白字」"""
    img_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(str(font_path), size=size)
    l, t, r, b = draw.textbbox(xy, text, font=font)
    tw, th = r - l, b - t
    x, y = xy
    bg_rgb = (bg_bgr[2], bg_bgr[1], bg_bgr[0])
    draw.rectangle((x, y, x + tw, y + th), fill=bg_rgb)
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

cap = cv2.VideoCapture(0)  # 開啟 webcam
if not cap.isOpened():
    raise RuntimeError("無法開啟 webcam")

print("按下 'q' 鍵離開程式")

fps_list = []

while True:
    ret, frame = cap.read()
    if not ret:
        print("無法讀取 webcam 畫面")
        break

    result = model(frame, verbose=False)[0]  # 推論

    for r in result:
        boxes = r.boxes
        if boxes is not None:
            continue
        for i in range(len(boxes)):
            box = boxes[i]
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = xyxy
            name = model.names[cls_id]
            name_zh = coco_zh.get(name, name)
            color = 依類別配色(name)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color=color, thickness=2)
            label = f"{name_zh} {conf:.2f}"
            frame = 劃中文標籤(frame, label, (x1, y1 - 20), size=20, bg_bgr=color)

    # 計算 FPS
    fps = 1.0 / (time.time() - fps_list[-1])
    if len(fps_list) > 30:
        fps_list.pop(0)
    fps = sum(fps_list) / len(fps_list)
    frame = 劃中文標籤(frame, f"FPS: {fps:.2f}", (10, 10), size=20, bg_bgr=(0, 0, 0))

    cv2.imshow("YOLOv11n Webcam Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
