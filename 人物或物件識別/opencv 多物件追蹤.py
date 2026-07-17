import cv2

multiTracker = cv2.legacy.MultiTracker_create()  # type: ignore[attr-defined] # 建立多物件追蹤器
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
    frame = cv2.resize(frame, (400, 230))
    keyName = cv2.waitKey(50)

    if keyName == ord('q'):
        break
    if keyName == ord('a'):
        for i in range(2):
            area = cv2.selectROI('test', frame, showCrosshair=False, fromCenter=False)
            # 標記外框後設定物件追蹤演算法
            tracker = cv2.legacy.TrackerCSRT_create()  # type: ignore[attr-defined]
            # 將該物件加入 multiTracker
            multiTracker.add(tracker, frame, area)
        # 設定 True 開始追蹤
        tracking = True
    if tracking:
        # 更新 multiTracker
        sucess, points = multiTracker.update(frame)
        a = 0
        if sucess:
            for i in points:
                p1 = (int(i[0]), int(i[1]))
                p2 = (int(i[0] + i[2]), int(i[1] + i[3]))
                # 標記物件外框
                cv2.rectangle(frame, p1, p2, colors[a], 3)
                a = a + 1
    cv2.imshow('test', frame)
cap.release()
cv2.destroyAllWindows()