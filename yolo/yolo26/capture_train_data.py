import cv2, os, time
from ultralytics import YOLO

# only save a frame when a detection confidence is below this, the model is unsure so it's a good training sample
CONF_THRESH = 0.5
# minimum frames between two saves, avoid saving near-duplicate frames of the same moment
COOLDOWN = 15

model = YOLO("yolo26n.pt")
camera = cv2.VideoCapture(0)

base = os.path.dirname(__file__)
img_dir, label_dir = os.path.join(base, "dataset", "images"), os.path.join(base, "dataset", "labels")

frame_idx, last_saved = 0, -COOLDOWN
while camera.isOpened():
    success, frame = camera.read()
    if not success:
        break

    result = model.track(frame, persist=True)[0]
    annotated = result.plot()
    cv2.imshow("Capture Training Data", annotated)

    boxes = result.boxes
    if boxes is not None and len(boxes) > 0:
        is_hard_sample = boxes.conf.min().item() < CONF_THRESH
        if is_hard_sample and frame_idx - last_saved >= COOLDOWN:
            name = f"{int(time.time() * 1000)}"
            cv2.imwrite(os.path.join(img_dir, f"{name}.jpg"), frame)

            h, w = frame.shape[:2]
            with open(os.path.join(label_dir, f"{name}.txt"), "w") as f:
                for cls, xywh in zip(boxes.cls.tolist(), boxes.xywh.tolist()):
                    x, y, bw, bh = xywh
                    f.write(f"{int(cls)} {x / w:.6f} {y / h:.6f} {bw / w:.6f} {bh / h:.6f}\n")

            last_saved = frame_idx
            print(f"saved hard sample: {name}")

    frame_idx += 1
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
