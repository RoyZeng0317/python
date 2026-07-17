import cv2

img = cv2.imread('daniel.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # 圖片轉換為灰階

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")  # type: ignore

# 設定集聯分類機器為人臉的模型
faces = face_cascade.detectMultiScale(gray)

for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow('人臉識別', img)
cv2.waitKey(0) # 按下任意鍵停止
cv2.destroyAllWindows()
# faces = face_cascade.detectMultiScale(img, scaleFactor, minNeighbors, flags, minSIze, maxSize)
# check and 取出相關屬性
# img 來源影像，使用灰階影像