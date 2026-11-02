from ultralytics import YOLO
import os

model = YOLO("yolo26n.pt")
base = os.path.dirname(__file__)

for f in ["2026-09-13 18-26-02.mp4", "2026-09-13 18-25-21.mp4"]: results = model.track(source=os.path.join(base, f), show=True,
                                                                                       tracker="bytetrack.yaml")