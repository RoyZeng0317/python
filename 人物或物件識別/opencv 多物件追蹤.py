import cv2

trackers = []  # OpenCV 5.0 已移除 MultiTracker,改用 list 手動管理多個追蹤器
tracking = False # 設定 False 表示未開始追蹤
colors = [(0, 0, 255), (0, 255, 255), (255, 255, 0)] # 建立外框顏色清單

cap = cv2.VideoCapture(0) # 讀取 camera
if not cap.isOpened():
    print("Can't open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame")
        break
    frame = cv2.resize(frame, (640, 450))
    keyName = cv2.waitKey(50)

    if keyName == ord('q'):
        break
    if keyName == ord('a'):
        for i in range(2):
            area = cv2.selectROI('test', frame, showCrosshair=False, fromCenter=False)
            # 標記外框後設定物件追蹤演算法(CSRT 已移除,改用 MIL)
            tracker = cv2.TrackerMIL_create()
            tracker.init(frame, area)
            trackers.append(tracker)
        # 設定 True 開始追蹤
        tracking = True
    if tracking:
        a = 0
        for tracker in trackers:
            # 逐一更新每個追蹤器
            sucess, box = tracker.update(frame)
            if sucess:
                p1 = (int(box[0]), int(box[1]))
                p2 = (int(box[0] + box[2]), int(box[1] + box[3]))
                # 標記物件外框
                cv2.rectangle(frame, p1, p2, colors[a], 3)
            a = a + 1
    cv2.imshow('test', frame)
cap.release()
cv2.destroyAllWindows()