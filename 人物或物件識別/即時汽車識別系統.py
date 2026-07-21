# opencv library
# ultralytics library
# pip install ultralytics

import os
import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'yolo11n.pt')  # repo 根目錄現成的預訓練模型

VEHICLE_CLASSES = {'car', 'truck', 'bus'}   # COCO 類別裡跟車輛相關的類別,只要 'car' 可以縮小這個集合
MAX_CAMERA_INDEX_TO_SCAN = 5                # 掃描本機攝影機(webcam / USB 攝影機)時嘗試的索引上限


def list_available_cameras(max_index: int = MAX_CAMERA_INDEX_TO_SCAN) -> list[int]:
    """掃描本機可用的攝影機索引。"""
    backend = cv2.CAP_DSHOW if os.name == 'nt' else cv2.CAP_ANY
    available: list[int] = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            available.append(index)
        cap.release()
    return available


def choose_input_source() -> int | str:
    """讓使用者選擇輸入裝置:本機攝影機,或手機的 IP 攝影機串流網址。"""
    cameras = list_available_cameras()

    print("可用的輸入裝置:")
    for i, cam_index in enumerate(cameras):
        print(f"  [{i}] 本機攝影機 (index={cam_index})")
    phone_option = len(cameras)
    print(f"  [{phone_option}] 手機攝影機 (需先在手機安裝 IP Webcam / DroidCam 等 App,輸入其串流網址)")

    choice = input(f"請選擇輸入裝置編號 (0-{phone_option}): ").strip()

    if choice.isdigit():
        choice_index = int(choice)
        if choice_index == phone_option:
            url = input("請輸入手機攝影機串流網址 (例如 http://192.168.1.50:8080/video): ").strip()
            if not url:
                raise ValueError("未輸入串流網址")
            return url
        if 0 <= choice_index < len(cameras):
            return cameras[choice_index]

    raise ValueError("無效的選擇")


def open_capture(source: int | str) -> cv2.VideoCapture:
    if isinstance(source, int) and os.name == 'nt':
        return cv2.VideoCapture(source, cv2.CAP_DSHOW)
    return cv2.VideoCapture(source)


def main() -> None:
    model = YOLO(MODEL_PATH)
    source = choose_input_source()

    cap = open_capture(source)
    if not cap.isOpened():
        raise RuntimeError(f"無法開啟輸入裝置: {source}")

    print("開始即時汽車辨識,按下 'q' 或 ESC 結束。")
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("讀取畫面失敗,結束。")
                break

            results = model(frame, verbose=False)[0]  # type: ignore[index]
            assert isinstance(results, Results)

            if results.boxes is not None:
                for box in results.boxes:
                    class_name = model.names[int(box.cls[0])]
                    if class_name not in VEHICLE_CLASSES:
                        continue
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)   # 繪製外框
                    cv2.putText(frame, f"{class_name} {confidence:.2f}", (x1, max(0, y1 - 8)),
                                cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

            cv2.imshow('即時汽車識別系統', frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):  # q 或 ESC
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
