"""
NFC 卡片讀取 - Python 端（Serial 通訊）
搭配 Arduino + PN532 或 RC522 使用

安裝依賴：pip install pyserial
"""

import serial
import serial.tools.list_ports
import time


def find_arduino(baudrate=115200, timeout=1):
    """自動尋找 Arduino 串口"""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"找到裝置: {port.device} - {port.description}")
    if ports:
        ser = serial.Serial(ports[0].device, baudrate, timeout=timeout)
        time.sleep(2)  # 等待 Arduino 重置
        return ser
    return None


def read_nfc_loop(ser):
    """持續讀取 NFC 卡片資料"""
    print("等待讀取 NFC 卡片...")
    print("將卡片靠近讀卡機即可\n")

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if line:
                    parse_nfc_data(line)
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n停止讀取")
            break


def parse_nfc_data(line):
    """解析 Arduino 回傳的資料"""
    if line.startswith("UID:"):
        uid = line[4:].strip()
        print(f"[卡片識別] UID: {uid}")
    elif line.startswith("TYPE:"):
        card_type = line[5:].strip()
        print(f"[卡片類型] {card_type}")
    elif line.startswith("DATA:"):
        data = line[5:].strip()
        print(f"[區塊資料] {data}")
    elif line.startswith("TEXT:"):
        text = line[5:].strip()
        print(f"[NDEF 文字] {text}")
    elif line.startswith("URL:"):
        url = line[5:].strip()
        print(f"[NDEF 網址] {url}")
    elif line.startswith("ERROR:"):
        error = line[6:].strip()
        print(f"[錯誤] {error}")
    elif line.startswith("READY"):
        print("[系統] 讀卡機就緒")
    else:
        print(f"[訊息] {line}")


def main():
    print("=" * 40)
    print("  NFC 卡片讀取工具")
    print("  Arduino + PN532 / RC522")
    print("=" * 40)
    print()

    ser = find_arduino()
    if ser is None:
        print("找不到 Arduino，請確認：")
        print("  1. USB 已連接")
        print("  2. Arduino IDE 已關閉（釋放串口）")
        print("  3. 驅動程式已安裝")
        return

    print(f"已連接: {ser.port}\n")
    read_nfc_loop(ser)
    ser.close()


if __name__ == "__main__":
    main()
