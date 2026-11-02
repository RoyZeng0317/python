# pip install opencv-python ultralytics
import cv2, os
from typing import List, cast
from ultralytics import YOLO
from ultralytics.engine.results import Results

model = YOLO("yolo26n.pt")
cap = cv2.VideoCapture(0)

os.makedirs("dataset/images", exist_ok=True)
os.makedirs("dataset/labels", exist_ok=True)

img_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = cast(List[Results], model(frame, conf=0.25, verbose=False))
    result = results[0]
    annotated_frame = result.plot()

    cv2.imshow("Real-Time YOLO - Press 's to Save Frame", annotated_frame)
    key = cv2.waitKey(1) & 0xFF
    # press 's' key: auto to save the current monitor and YOLO format label file
    if key == ord('s'):
        img_name = f"frame_{img_count:04d}"

        # 01. save the img
        cv2.imwrite(f"dataset/images/{img_name}.jpg", frame)

        # 02. save the YOLO auto label (.txt)
        h, w, _ = frame.shape
        with open(f"dataset/labels/{img_name}.txt", "w") as f:
            boxes = result.boxes if result.boxes is not None else []
            for box in boxes:
                cls_id = int(box.cls[0])
                # get the together [x_center. y_center, width, height]
                x, y, bw, bh = box.xywh[0].tolist()
                f.write(f"{cls_id}{x:.6f}{y:.6f}{bw:.6f}{bh:.6f}\n")

        print(f"alrady to save the label picture: {img_name}")
        img_count += 1

    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()