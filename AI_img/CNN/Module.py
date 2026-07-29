# -*- coding: utf-8 -*-
"""
簡易 CNN 影像分類器 (PyTorch)
教學用途：從零手刻卷積神經網路 (CNN)，理解卷積/池化/全連接、以及訓練迴圈 (forward -> loss -> backward -> step) 的原理
資料集格式：ImageFolder 風格 -> DATA_DIR/類別A/*.jpg, DATA_DIR/類別B/*.jpg, ...
"""

import random

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

# 模型訓練參數
Epchs = 5
Batch_Size = 32
lr = 0.0003
Img_Size = 224
seed = 42

# 資料集路徑：尚未確定要用哪個資料集，請指向 ImageFolder 格式的資料夾
# 例如："../人物或物件識別/mask"（底下需有「戴口罩」「沒戴口罩」等分類子資料夾）
DATA_DIR = ""


class SimpleCNN(nn.Module):
    """
    從零手刻的簡單 CNN
    架構：(卷積 -> ReLU -> 池化) x 3 -> 攤平 -> 全連接 -> 輸出各類別分數
    """

    def __init__(self, num_classes):
        super().__init__()
        # 卷積層：用小範圍濾波器 (kernel) 在圖片上滑動，抽取邊緣/顏色/紋理等局部特徵
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        # 池化層：把特徵圖邊長縮小一半，保留主要特徵、降低運算量，也讓模型對些微位移更穩健
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

        # 經過 3 次池化 (每次邊長減半)，特徵圖邊長會變成 Img_Size / 8
        feat_size = Img_Size // 8
        self.fc1 = nn.Linear(64 * feat_size * feat_size, 128)
        self.fc2 = nn.Linear(128, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 第一層：抓邊緣、顏色等低階特徵
        x = self.pool(F.relu(self.conv2(x)))  # 第二層：組合成紋理、局部形狀等中階特徵
        x = self.pool(F.relu(self.conv3(x)))  # 第三層：組合成更接近物件輪廓的高階特徵
        x = torch.flatten(x, 1)               # 攤平成一維向量，準備丟進全連接層
        x = F.relu(self.fc1(x))
        x = self.dropout(x)                   # 訓練時隨機關閉部分神經元，避免過度擬合 (overfitting)
        x = self.fc2(x)                       # 輸出每個類別的分數 (logits)
        return x


def build_dataloaders(data_dir):
    """
    讀取 ImageFolder 格式的資料集，並切分成訓練集 / 驗證集
    規則：data_dir 底下每個子資料夾代表一個分類，資料夾內放該分類的圖片
    """
    transform = transforms.Compose([
        transforms.Resize((Img_Size, Img_Size)),
        transforms.ToTensor(),  # 圖片轉成 Tensor，並把像素值從 0~255 正規化到 0~1
    ])

    dataset = datasets.ImageFolder(root=data_dir, transform=transform)

    val_ratio = 0.2
    val_size = int(len(dataset) * val_ratio)
    train_size = len(dataset) - val_size
    train_set, val_set = random_split(
        dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(seed),
    )

    train_loader = DataLoader(train_set, batch_size=Batch_Size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=Batch_Size, shuffle=False)
    return train_loader, val_loader, dataset.classes


def train_one_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    correct = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()             # 清空上一批次殘留的梯度
        outputs = model(images)           # 前向傳播 (forward)：算出預測分數
        loss = criterion(outputs, labels) # 計算預測與正確答案的誤差 (loss)
        loss.backward()                   # 反向傳播 (backward)：算出每個參數對 loss 的梯度
        optimizer.step()                  # 依梯度更新參數，讓 loss 逐步變小

        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()

    avg_loss = total_loss / len(loader.dataset)
    accuracy = correct / len(loader.dataset)
    return avg_loss, accuracy


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    correct = 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()

    avg_loss = total_loss / len(loader.dataset)
    accuracy = correct / len(loader.dataset)
    return avg_loss, accuracy


if __name__ == "__main__":
    if not DATA_DIR:
        raise ValueError("請先設定 DATA_DIR，指向 ImageFolder 格式的資料集資料夾")

    random.seed(seed)
    torch.manual_seed(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    train_loader, val_loader, classes = build_dataloaders(DATA_DIR)
    print(f"分類類別: {classes}")

    model = SimpleCNN(num_classes=len(classes)).to(device)
    criterion = nn.CrossEntropyLoss()  # 多分類常用的損失函數
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    for epoch in range(1, Epchs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, criterion, device)
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        print(
            f"Epoch {epoch}/{Epchs} | "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )
