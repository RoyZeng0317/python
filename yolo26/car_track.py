import cv2, os
from typing import cast
from ultralytics import YOLO
from ultralytics.engine.results import Results

model = YOLO("yolo26n.pt")
cap = cv2.VideoCapture(0)

os.makedirs("dataset/images", exist_ok=True)
os.makedirs("dataset/labels", exist_ok=True)

img_count = 0

while cap.isOpened:
    ret, frame = cap.read()

    if not  ret:
        print("Can't get the picture, finished to stream.")
        break

    results = cast(list[Results], model(frame, conf=0.25, verbose=False))
    annotated_frame = results[0].plot()

    cv2.imshow("Real-Time YOLO - Press 's' to Save Frame", annotated_frame)
    key = cv2.waitKey(1) & 0xFF
    
    cv2.imshow("Frame", frame)

    if key == ord('s'):
        img_name = f"frame_{img_count:04d}"

        # 01. save the img
        cv2.imwrite(f"dataset/images/{img_name}.jpg", frame)

        # 02. save YOLO auto label (.txt)
        h, w, _ = frame.shape
        with open(f"dataset/labels/{img_name}.txt", "w") as f:
            boxes = results[0].boxes
            for box in boxes if boxes is not None else []:
                cls_id = int(box.cls[0])
                # get the 
                x, y, bw, bh = box.xywhn[0].tolist()
                f.write(f"{cls_id} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}\n")

            print(f"Already to save the marked picture: {img_name}")
            img_count += 1

    elif key == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()