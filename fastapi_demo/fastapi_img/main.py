# 啟動伺服器
# fastapi dev main.py
# 用 streaming response
# pip install pillow
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw
from io import BytesIO

app = FastAPI()

@app.get("/image")
def get_image():
    return FileResponse(
        path="img/penguins.jpg",
        media_type="image/jpeg",
        filename="download.jpg",
        content_disposition_type="attachment"
    )

@app.get("/generate-image")
def generate_image():
    image = Image.new("RGB", (400, 200), "white")

    draw = ImageDraw.Draw(image)
    draw.rectangle((50, 50, 350, 150,), fill="blue")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(
        buffer,
         media_type="image/png"
    )