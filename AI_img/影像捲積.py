# -*- coding: utf-8 -*-
# 匯入庫
import cv2
import matplotlib.pyplot as plt, numpy as np

# 讓 matplotlib 標題可以正確顯示中文，避免變成方框
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 缺乏疑似 UTF-8 中文編碼格式 -> 已確認檔案為 UTF-8（無 BOM），並補上明確的 coding 宣告

def imread_unicode(path, flags=cv2.IMREAD_COLOR):
    """支援中文路徑的圖片讀取 (Windows 上 cv2.imread 對中文路徑常會失敗)"""
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, flags)


def convolve2d(image, kernel):
    """手刻 2D 卷積：zero padding，輸出尺寸與輸入相同"""
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")
    output = np.zeros_like(image, dtype=np.float32)

    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            region = padded[y:y + kh, x:x + kw]
            output[y, x] = np.sum(region * kernel)

    # 依照 kernel 權重總和做正規化，避免亮度爆掉
    k_sum = kernel.sum()
    if k_sum != 0:
        output /= k_sum

    return np.clip(output, 0, 255).astype(np.uint8)


# 圖像位置
path = "Ai_img/蒙娜麗莎.jpg"  # 可自行更換成其他圖片路徑

# 卷積值
Kenernel = [
    [1, 0, 1],
    [0, 1, 0],
    [1, 1, 0]
]


if __name__ == "__main__":
    img = imread_unicode(path)
    if img is None:
        raise FileNotFoundError(f"找不到圖片: {path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.array(Kenernel, dtype=np.float32)
    result = convolve2d(gray, kernel)

    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    plt.title("原始圖片")
    plt.imshow(gray, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.title("卷積後圖片")
    plt.imshow(result, cmap="gray")
    plt.axis("off")

    plt.tight_layout()
    # 顯示輸出結果
    plt.show()
