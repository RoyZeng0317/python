# pip install easyocr
import easyocr

# init, use the zh-tw to recongizion
reader = easyocr.Reader(['ch_tra', 'en'])
img_path = 'road_sign.jpg'
results = reader.readtext(img_path)

for idx, (box, text, confidence) in enumerate(results):
    # box: text area location (4 corner points)
    # text: recognized string
    # confidence: recognition confidence
    print(f"[{confidence:.2f}] {text}")