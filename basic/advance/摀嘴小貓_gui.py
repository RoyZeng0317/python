import cv2
import tkinter as tk
from PIL import Image, ImageTk

VIDEO_PATH = "C:\\Users\\roy\\Documents\\GitHub\\python\\basic\\advance\\video.mp4"
PIXEL_SIZE = 15
SKIP_FRAME = 5
FRAME_DELAY_MS = 125
DISPLAY_SCALE = 10  # 每個像素塊放大成多少螢幕像素


class PixelVideoApp:
    def __init__(self, root, video_path):
        self.root = root
        self.root.title("摀嘴小貓")

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise IOError(f"無法開啟影片: {video_path}")

        self.frame_idx = 0
        self.photo = None

        self.label = tk.Label(root, bg="black")
        self.label.pack()

        self.update_frame()

    def frame_to_pixel(self, frame):
        h, w = frame.shape[:2]
        frame = cv2.resize(frame, (w // 5 * 4, h // 5 * 4))
        h, w = frame.shape[:2]
        small = cv2.resize(
            frame,
            (max(1, w // PIXEL_SIZE), max(1, h // PIXEL_SIZE)),
            interpolation=cv2.INTER_NEAREST,
        )
        big = cv2.resize(
            small,
            (small.shape[1] * DISPLAY_SCALE, small.shape[0] * DISPLAY_SCALE),
            interpolation=cv2.INTER_NEAREST,
        )
        return big

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.frame_idx = 0
            self.root.after(FRAME_DELAY_MS, self.update_frame)
            return

        show = self.frame_idx % SKIP_FRAME == 0
        if show:
            pixelated = self.frame_to_pixel(frame)
            rgb = cv2.cvtColor(pixelated, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self.photo = ImageTk.PhotoImage(image=img)
            self.label.configure(image=self.photo)

        self.frame_idx += 1
        self.root.after(FRAME_DELAY_MS if show else 1, self.update_frame)

    def on_close(self):
        self.cap.release()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = PixelVideoApp(root, VIDEO_PATH)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
