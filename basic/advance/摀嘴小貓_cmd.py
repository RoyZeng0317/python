import cv2
import time
import os
from rich.console import Console
from rich.text import Text

BLOCK = " "
console = Console()

VIDEO_PATH = "C:\\Users\\roy\\Documents\\GitHub\\python\\basic\\advance\\video.mp4"
PIXEL_SIZE = 15
SKIP_FRAME = 5
FRAME_DELAY = 0.125

def frame_to_pixel(frame, pixel_size):
    frame = cv2.resize(
        frame,
        (frame.shape[:2][1] // 5 * 4, frame.shape[:2][0] // 5 * 4)
    )
    h, w = frame.shape[:2]
    small = cv2.resize(
        frame,
        (w // pixel_size, h // pixel_size),
        interpolation=cv2.INTER_NEAREST
        )
    return small
def video_to_pixel(video_path, pixel_size, skip_frame):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % skip_frame == 0:
            yield frame_to_pixel(frame, pixel_size)
        frame_idx += 1
    cap.release()

def build_frame_buffer(img):
    h, w = img.shape[:2]
    fix_h = max(1, int(h * 0.5))
    img = cv2.resize(img, (w, fix_h), interpolation=cv2.INTER_NEAREST)
    h, w = img.shape[:2]
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    full_frame = Text()
    for y in range(h):
        line_text = Text()
        row_data = img_rgb[y]
        for x in range(w):
            r, g, b, = row_data[x]
            line_text.append(BLOCK, style=f"on rgb({r},{g},{b})")
        line_text.append("\n")
        full_frame.append(line_text)
    return full_frame, h

def main():
    os.system("cls")

    prev_lines = 0

    for img in video_to_pixel(VIDEO_PATH, PIXEL_SIZE, SKIP_FRAME):
        frame_text, line_cnt = build_frame_buffer(img)

        if prev_lines > 0:
            print("\033[A" * prev_lines, end="")

        console.print(frame_text, end="")
        prev_lines = line_cnt

        time.sleep(FRAME_DELAY)

if __name__ == "__main__":
    main()