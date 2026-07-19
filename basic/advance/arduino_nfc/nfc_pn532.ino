/*
 * NFC 讀取 - PN532 模組 (I2C 連接)
 * 
 * 硬體接線 (Arduino Uno/Nano):
 *   PN532 SDA  -> A4
 *   PN532 SCL  -> A5
 *   PN532 VCC  -> 3.3V
 *   PN532 GND  -> GND
 *   PN532 IRQ  -> (可不接)
 *
 * 安裝函式庫: Arduino IDE -> 工具 -> 管理函式庫
 *   搜尋 "Adafruit PN532" 並安裝
 *   同時安裝依賴 "Adafruit BusIO"
 */

#include <Wire.h>
#include <Adafruit_PN532.h>

// I2C 接腳
#define PN532_SDA  (A4)
#define PN532_SCL  (A5)

Adafruit_PN532 nfc(PN532_SDA, PN532_SCL);

void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);

    nfc.begin();

    uint32_t versiondata = nfc.getFirmwareVersion();
    if (!versiondata) {
        Serial.println("ERROR:找不到 PN532 模組，請檢查接線");
        while (1) delay(100);
    }

    Serial.print("PN532 版本: ");
    Serial.print((versiondata >> 16) & 0xFF, HEX);
    Serial.print(".");
    Serial.println((versiondata >> 8) & 0xFF, HEX);

    nfc.SAMConfig();
    Serial.println("READY");
}

void loop() {
    uint8_t uid[7];
    uint8_t uidLength;

    // 等待卡片
    if (nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength)) {

        // 輸出 UID
        Serial.print("UID:");
        for (uint8_t i = 0; i < uidLength; i++) {
            if (uid[i] < 0x10) Serial.print("0");
            Serial.print(uid[i], HEX);
        }
        Serial.println();

        // 輸出卡片類型
        Serial.print("TYPE:");
        if (uidLength == 4) {
            Serial.println("Mifare Classic / Ultralight (4 bytes)");
        } else if (uidLength == 7) {
            Serial.println("Mifare DESFire (7 bytes)");
        } else {
            Serial.print(uidLength);
            Serial.println(" bytes");
        }

        // 嘗試讀取 NDEF 資訊 (Mifare Ultralight / NTAG)
        if (uidLength == 4) {
            readNDEF();
        }

        delay(1000);  // 防止重複讀取
    }
}

void readNDEF() {
    // 嘗試讀取前幾個頁面的 NDEF 資料
    uint8_t ndefHeader[4];
    uint8_t data[16];

    // 嘗試讀取頁面 4 (NDEF 資料起始)
    if (nfc.ntag2xx_ReadPage(4, data)) {
        // 檢查是否為 NDEF 訊息
        if (data[0] == 0x03) {
            uint8_t ndefLength = data[1];

            if (data[2] == 0xD1) {  // NDEF 訊息 (MB=1, ME=1, SR=1)
                uint8_t recordType = data[3];

                if (recordType == 0x01) {  // TNF=Well Known, Type=R (Text)
                    Serial.print("TEXT:");
                    uint8_t langLen = data[5] & 0x3F;
                    for (uint8_t i = 6 + langLen; i < 4 + ndefLength && i < 16; i++) {
                        Serial.print((char)data[i]);
                    }
                    Serial.println();
                }
                else if (recordType == 0x02) {  // TNF=Well Known, Type=U (URL)
                    Serial.print("URL:");
                    const char* prefix = "";
                    if (data[6] == 0x01) prefix = "http://www.";
                    else if (data[6] == 0x02) prefix = "https://www.";
                    else if (data[6] == 0x03) prefix = "http://";
                    else if (data[6] == 0x04) prefix = "https://";
                    Serial.print(prefix);
                    for (uint8_t i = 7; i < 4 + ndefLength && i < 16; i++) {
                        Serial.print((char)data[i]);
                    }
                    Serial.println();
                }
            }
        }

        // 輸出原始區塊資料
        Serial.print("DATA:");
        for (uint8_t i = 0; i < 4; i++) {
            if (data[i] < 0x10) Serial.print("0");
            Serial.print(data[i], HEX);
            Serial.print(" ");
        }
        Serial.println();
    }
}
