# 需執行: pip install numpy torch torchvision matplotlib
from typing import Any

import torch
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from torchvision import transforms
from torchvision.datasets import MNIST
# 神經網路主軸
class Net(torch.nn.Module):
    # 初始化
    def __init__(self):
        super().__init__()
        # 四個全連接層
        self.fc1 = torch.nn.Linear(28 * 28, 64)     # 圖片大小為 28 * 28 pixel
        self.fc2 = torch.nn.Linear(64, 64)          # 三個各 64 個節點
        self.fc3 = torch.nn.Linear(64, 64)
        self.fc4 = torch.nn.Linear(64, 10)          # 同樣 64 個節點，輸出 10 個類別
    # 定義前向傳播過程(x 是圖片輸入)
    def forward(self, x):
        x = torch.nn.functional.relu(self.fc1(x))   # 統一先做全連接線性計算
        x = torch.nn.functional.relu(self.fc2(x))
        x = torch.nn.functional.relu(self.fc3(x))
        x = torch.nn.functional.log_softmax(self.fc4(x), dim=1) # 輸出層用 softmax 歸化(log_softmax 提高輸出的穩定性)
        return x
# 導入數據資料
def get_data_loader(is_train):
    to_tensor = transforms.Compose([transforms.ToTensor()])     # 多維數據值
    data_set = MNIST("", is_train, transform=to_tensor, download=True) #下載 MNIST 的數據集， "" 表示下載資料夾(空值為目前的資料夾)，is_train 是指導入訓練集還是測試集
    return DataLoader(data_set, batch_size=15, shuffle=True)    # batch_size 是一次訓練 15 張圖片， shuffle 是指打亂順序(表示回傳數據重新載入)
# 評估神經網路的識別正確率
def evaluate(test_data, net):
    n_correct = 0
    n_total = 0
    with torch.no_grad():
        for(x, y) in test_data:     # 從測試集按批次取數據資料
            outputs = net.forward(x.view(-1, 28 * 28))  # 計算神經網路的預測值
            # 對批次中的每個結果進行比較
            for i, output in enumerate(outputs):
                if torch.argmax(output) == y[i]:    # argmax 計算一個數列中最大值的序號(預測手寫結果)
                    n_correct += 1  # 累加正確的數量
                n_total += 1
    return n_correct / n_total  # 回傳正確率

def main():
    # 初始化神經網路
    train_data = get_data_loader(is_train=True)     # 導入訓練集
    test_data = get_data_loader(is_train=False)     # 導入測試集
    net = Net()
    # 輸出初始網路的正確率，正常值為 0.1
    print("inital accuracy:", evaluate(test_data, net))
    # 訓練神經網路
    optimizer = torch.optim.Adam(net.parameters(), lr=0.01)
    for epoch in range(2):
        for(x, y) in train_data:    # 一個數據集當中反覆訓練神經網路數次
            net.zero_grad()     # 初始化
            output = net.forward(x.view(-1, 28 * 28))   # 正向傳播
            loss = torch.nn.functional.nll_loss(output, y)  # 計算誤差值(nll_loss 是對數損失函數，與 log_softmax中的對數運算做配對)
            loss.backward()     # 反向誤差值傳播
            optimizer.step()    # 提高網路參數
        print("epoch", epoch, "accuracy:", evaluate(test_data, net))    # 輸出當前網路的正確率
    # 訓練完成後
    for(n, (x, _)) in enumerate(test_data):
        if n > 3:   # 隨機抽三張圖片
            break
        predict = torch.argmax(net.forward(x[0].view(-1, 28 * 28)))
        plt.figure(n)
        plt.imshow(x[0].view(28, 28))
        plt.title("prediction: " + str(int(predict)))
    plt.show()  # 顯示網路的預測結果
# 執行主程式
if __name__ == "__main__":
    main()