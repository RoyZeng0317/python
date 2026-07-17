import os
import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(SCRIPT_DIR, 'cars.webp')
MODEL_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'yolo11n.pt')  # repo 根目錄現成的預訓練模型

VEHICLE_CLASSES = {'car', 'truck', 'bus'}   # COCO 類別裡跟車輛相關的類別,只要 'car' 可以縮小這個集合

img = cv2.imread(IMAGE_PATH)
if img is None:
    raise FileNotFoundError(f"讀不到圖片: {IMAGE_PATH}")

model = YOLO(MODEL_PATH)
# model() 的型別標註是 Iterator[Results | Tensor] | list[Results] | list[Tensor],
# 因為 ultralytics 同一個方法在 stream=True 時回傳迭代器、追蹤模式會回傳 Tensor。
# 這裡是預設的 stream=False 一般偵測,實際上一定是 list[Results],用 isinstance narrow 掉其他可能性。
results = model(img)[0]  # type: ignore[index]
assert isinstance(results, Results)

if results.boxes is not None:
    for box in results.boxes:
        class_name = model.names[int(box.cls[0])]
        if class_name not in VEHICLE_CLASSES:
            continue
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)   # 繪製外框
        cv2.putText(img, f"{class_name} {confidence:.2f}", (x1, max(0, y1 - 8)),
                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

cv2.imshow('test', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
