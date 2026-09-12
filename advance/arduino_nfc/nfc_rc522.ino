/*
 * NFC 讀取 - RC522 (MFRC522) 模組
 * 
 * 硬體接線 (Arduino Uno/Nano):
 *   RC522 SDA  -> D10
 *   RC522 SCK  -> D13
 *   RC522 MOSI -> D11
 *   RC522 MISO -> D12
 *   RC522 RST  -> D9
 *   RC522 3.3V -> 3.3V
 *   RC522 GND  -> GND
 *
 * 安裝函式庫: Arduino IDE -> 工具 -> 管理函式庫
 *   搜尋 "MFRC522" by miguelbalboa 並安裝
 */

#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN   9
#define SS_PIN    10

MFRC522 rfid(SS_PIN, RST_PIN);
MFRC522::MIFARE_Key key;

void setup() {
    Serial.begin(115200);
    while (!Serial) delay(10);

    SPI.begin();
    rfid.PCD_Init();
    delay(100);

    // 設定預設密鑰 (FFFFFFFFFFFF)
    for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF;
    }

    Serial.print("RC522 版本: ");
    Serial.print(rfid.PCD_ReadRegister(rfid.VersionReg), HEX);
    Serial.println();
    Serial.println("READY");
}

void loop() {
    // 檢測新卡片
    if (!rfid.PICC_IsNewCardPresent()) return;
    if (!rfid.PICC_ReadCardSerial()) return;

    // 輸出 UID
    Serial.print("UID:");
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) Serial.print("0");
        Serial.print(rfid.uid.uidByte[i], HEX);
    }
    Serial.println();

    // 輸出卡片類型
    Serial.print("TYPE:");
    MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
    switch (piccType) {
        case MFRC522::PICC_TYPE_MIFARE_MINI:
            Serial.println("Mifare Mini (320 bytes)");
            break;
        case MFRC522::PICC_TYPE_MIFARE_1K:
            Serial.println("Mifare Classic 1K");
            break;
        case MFRC522::PICC_TYPE_MIFARE_4K:
            Serial.println("Mifare Classic 4K");
            break;
        case MFRC522::PICC_TYPE_MIFARE_UL:
            Serial.println("Mifare Ultralight");
            break;
        case MFRC522::PICC_TYPE_MIFARE_DESFIRE:
            Serial.println("Mifare DESFire");
            break;
        default:
            Serial.println("未知類型");
            break;
    }

    // 嘗試讀取 Mifare Classic 區塊資料
    if (piccType == MFRC522::PICC_TYPE_MIFARE_1K ||
        piccType == MFRC522::PICC_TYPE_MIFARE_4K) {
        readMifareBlocks();
    }

    // 嘗試讀取 Ultralight / NTAG 頁面
    if (piccType == MFRC522::PICC_TYPE_MIFARE_UL) {
        readUltralightPages();
    }

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    delay(1000);
}

void readMifareBlocks() {
    byte buffer[18];
    byte size = sizeof(buffer);
    byte trailerBlock = 7;

    // 認證扇區 0 的 Key A
    MFRC522::StatusCode status = rfid.PCD_Authenticate(
        MFRC522::PICC_CMD_MF_AUTH_KEY_A,
        trailerBlock,
        &key,
        &(rfid.uid)
    );

    if (status != MFRC522::STATUS_OK) {
        Serial.println("ERROR:密鑰認證失敗，可能需要不同的密鑰");
        return;
    }

    // 讀取扇區 0 的資料區塊 (1, 2, 3)
    for (byte block = 1; block <= 3; block++) {
        status = rfid.MIFARE_Read(block, buffer, &size);
        if (status == MFRC522::STATUS_OK) {
            Serial.print("DATA:區塊");
            Serial.print(block);
            Serial.print(": ");
            for (byte i = 0; i < 16; i++) {
                if (buffer[i] < 0x10) Serial.print("0");
                Serial.print(buffer[i], HEX);
                Serial.print(" ");
            }
            Serial.println();
        }
    }
}

void readUltralightPages() {
    byte buffer[4];

    // Ultralight/NTAG 從頁面 4 開始是 NDEF 資料
    for (byte page = 4; page <= 6; page++) {
        MFRC522::StatusCode status = rfid.MIFARE_Ultralight_ReadPage(page, buffer);
        if (status == MFRC522::STATUS_OK) {
            Serial.print("DATA:頁面");
            Serial.print(page);
            Serial.print(": ");
            for (byte i = 0; i < 4; i++) {
                if (buffer[i] < 0x10) Serial.print("0");
                Serial.print(buffer[i], HEX);
                Serial.print(" ");
            }
            Serial.println();

            // 檢查 NDEF 訊息
            if (page == 4 && buffer[0] == 0x03) {
                byte ndefLen = buffer[1];
                byte ndefData[16];
                byte idx = 0;

                // 跨頁面讀取完整 NDEF 訊息
                for (byte p = 4; p <= 4 + (ndefLen / 4) + 1 && p <= 12; p++) {
                    rfid.MIFARE_Ultralight_ReadPage(p, buffer);
                    for (byte i = 0; i < 4; i++) {
                        if (idx < sizeof(ndefData)) {
                            ndefData[idx++] = buffer[i];
                        }
                    }
                }

                // 解析 NDEF 記錄
                if (ndefLen > 2 && ndefData[2] == 0xD1) {
                    byte recordType = ndefData[3];

                    if (recordType == 0x01) {  // Text
                        Serial.print("TEXT:");
                        byte langLen = ndefData[5] & 0x3F;
                        for (byte i = 6 + langLen; i < 4 + ndefLen && i < idx; i++) {
                            Serial.print((char)ndefData[i]);
                        }
                        Serial.println();
                    }
                    else if (recordType == 0x02) {  // URL
                        Serial.print("URL:");
                        const char* prefix = "";
                        if (ndefData[6] == 0x01) prefix = "http://www.";
                        else if (ndefData[6] == 0x02) prefix = "https://www.";
                        else if (ndefData[6] == 0x03) prefix = "http://";
                        else if (ndefData[6] == 0x04) prefix = "https://";
                        Serial.print(prefix);
                        for (byte i = 7; i < 4 + ndefLen && i < idx; i++) {
                            Serial.print((char)ndefData[i]);
                        }
                        Serial.println();
                    }
                }
            }
        }
    }
}
