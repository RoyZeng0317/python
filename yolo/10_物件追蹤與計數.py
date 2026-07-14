# 10 - 物件追蹤與計數 (在 07/08 的即時推論基礎上,加上「追蹤 ID」與「越線計數」)
# 適合當作 09 CCTV 專題的延伸:例如統計有多少人/車經過畫面中的某一條線
#
# 前置需求:
#   pip install ultralytics opencv-python lap        (lap 是 ByteTrack 追蹤器需要的套件)
# 這支腳本不一定要先跑過 05 訓練:
#   - 如果有練好的 best.pt (runs/ 底下),會自動使用你自己的模型
#   - 找不到的話,會自動改用官方 yolo11n.pt (第一次執行自動下載),可以先體驗抓 COCO 常見物件(person, car ...)
#
# 玩法:
#   畫面中間會有一條紅線,物件的追蹤框「中心點」從線的一側移到另一側時,IN / OUT 計數會 +1
#   按 q 離開,按 s 存目前畫面 snapshot.png,離開時會印出各類別的統計報表

from collections import defaultdict
from pathlib import Path

import cv2
from ultralytics import YOLO

BASE = Path(__file__).parent

SOURCE = 0              # 0 = 預設 webcam;測試時可以改成影片路徑,例如 "test.mp4"
LINE_Y_RATIO = 0.5      # 計數線的位置(畫面高度的比例),0.5 = 正中間


def load_model():
    """優先使用 05 訓練出來的 best.pt,找不到就退回官方預訓練模型"""
    search_dirs = [BASE / "runs", BASE.parent.parent / "runs"]
    candidates = []
    for d in search_dirs:
        if d.exists():
            candidates.extend(d.rglob("best.pt"))
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)

    if candidates:
        model_path = candidates[0]
        print(f"使用自己訓練的模型: {model_path}")
        return YOLO(str(model_path))

    print("找不到自己訓練的模型(best.pt),改用官方預訓練模型 yolo11n.pt")
    print("(先跑 05_訓練我的 yolo11n.py 練出自己的模型後,重新執行這支就會自動改用你的模型)")
    return YOLO("yolo11n.pt")


def color_for(name):
    """依類別名稱決定一個固定的顏色,同一類別畫面上顏色一致"""
    h = hash(name) & 0xFFFFFF
    return (h & 0xFF, (h >> 8) & 0xFF, (h >> 16) & 0xFF)


def main(source=SOURCE, show=True):
    model = load_model()
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"無法開啟影像來源: {source}")

    line_y = None
    prev_side = {}   # track_id -> 目前在線的哪一側 ("up" / "down")
    counts = defaultdict(lambda: {"in": 0, "out": 0})  # 類別名稱 -> 進/出次數

    print("按 q 離開; 按 s 存目前畫面 snapshot.png")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if line_y is None:
            line_y = int(frame.shape[0] * LINE_Y_RATIO)

        results = model.track(frame, persist=True, tracker="bytetrack.yaml", verbose=False)
        boxes = results[0].boxes

        if boxes is not None and boxes.id is not None:
            ids = boxes.id.int().tolist()
            for i, track_id in enumerate(ids):
                x1, y1, x2, y2 = boxes.xyxy[i].tolist()
                name = model.names[int(boxes.cls[i])]
                cy = (y1 + y2) / 2
                side = "down" if cy >= line_y else "up"

                last_side = prev_side.get(track_id)
                if last_side is not None and last_side != side:
                    counts[name]["in" if side == "down" else "out"] += 1
                prev_side[track_id] = side

                color = color_for(name)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f"{name}#{track_id}", (int(x1), max(0, int(y1) - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.line(frame, (0, line_y), (frame.shape[1], line_y), (0, 0, 255), 2)

        total_in = sum(c["in"] for c in counts.values())
        total_out = sum(c["out"] for c in counts.values())
        cv2.putText(frame, f"IN {total_in}  OUT {total_out}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        if show:
            cv2.imshow("YOLO 物件追蹤與計數", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                cv2.imwrite("snapshot.png", frame)
                print("已存 snapshot.png")

    cap.release()
    if show:
        cv2.destroyAllWindows()

    total_in = sum(c["in"] for c in counts.values())
    total_out = sum(c["out"] for c in counts.values())
    print()
    print("=" * 60)
    print("統計結果")
    print("=" * 60)
    for name, c in counts.items():
        print(f"    {name:15s}  進 {c['in']:3d}  出 {c['out']:3d}")
    print(f"    {'總計':15s}  進 {total_in:3d}  出 {total_out:3d}")


if __name__ == "__main__":
    main()
