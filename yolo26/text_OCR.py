# pip install pytesseract pillow opencv-python


import cv2, pytesseract, os, numpy as np

path = os.path.join(os.path.dirname(__file__), "2026-08-26 023513.png")

# if are not let the Tesseract to add the system path, need to munal to define at the exe lcoation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 01. read the image
img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)

if img is None:
    raise FileNotFoundError("Can't read the image, please check the file path.")

# 02. image (gray + 2) to updating the recongizion
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# 03. running the OCR recongizion (chi_tra means zh_tw, eng means en_us)
text = pytesseract.image_to_string(thresh, lang='chi_tra+eng')

print("Recongizion result:\n", text)