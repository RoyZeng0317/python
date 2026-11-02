# pip isntall easyocr
import cv2, easyocr, os, numpy as np

path = os.path.join(os.path.dirname(__file__), "2026-08-26 023513.png")

img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
if img is None:
    raise FileNotFoundError("Can't read the img, check the file path.")

# create the EasyOCR recoginizion machine (zh-tw + en_us), first time to running it will be auto download the model
reader = easyocr.Reader(['ch_tra', 'en'])

result = reader.readtext(img, detail=0)

print("Recongizion reuslt:\n", "\n".join(str(item) for item in result))