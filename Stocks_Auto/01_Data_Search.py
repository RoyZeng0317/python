# [SUPERSEDED / 僅供參考] 這是使用者最初的手寫草稿，內含寫死的他機路徑
# （C:\Users\roy\...）與單一寫死的 YouTube 影片ID，皆已被 team-run/PLAN.md
# 的正式決策取代。實際可執行的管線入口點是 03_Pipeline.py，設定值已集中到
# config.py，來源清單見 config.SOURCES，規則見 rules.md/rules.py。
# 本檔不再被 03_Pipeline.py 呼叫或 import，保留純粹作為原始需求的歷史紀錄，
# 不要修改此檔案的邏輯來源生產結果 —— 請改到 03_Pipeline.py / fetch_*.py。
#
# 自動搜尋新聞
url = ["https://tw.stock.yahoo.com/", "https://www.youtube.com/watch?v=1I2iq41Akmo"] # 資料來源，第二個需要取台北時間 GT+8 09:00 - 13:00 的資料
# 目的資料夾
path = "C:\\Users\\roy\\Documents\\GitHub\\Websites\\Stocks\\backend\\data\\"
# 檔案名稱
file_name = "yyyy-mm--dd.json"
# 執行時間
start_time = "15:00"

rules = "rules.md"

# 資料分析

