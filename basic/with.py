
with open('data.txt', 'r', encoding='utf-8') as file:
    content = file.read()
# 離開 with 縮排區塊，系統會自動呼叫 file.close()