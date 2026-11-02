from pathlib import Path

# path = Path("data") / "sample.txt"
# print(path)
# print(Path.cwd())   # 資料夾位置
# print(__file__)     # 檔案位置
# script_path = Path(__file__)    # 字符串轉成位置對象
# script_path = script_path.resolve()    # 絕對位置
# path.exists()   # 檢查 path 儲存的檔案是否存在
# path.is_file()  # 是否是檔案格式

BASE = Path(__file__).resolve().parent
path = BASE / "data" / "sample.txt"
txt = path.read_text(encoding="utf-8")  # 常見文字編碼: ANSL、utf-8
print(txt)

output = BASE / "output"    # 輸出的資料夾
output.mkdir(parents=True, exist_ok=True)   # 建立輸出資料夾(parents是缺少父目錄時一起建立，exist_ok是資料夾存在也能不會輸出錯誤)
(output / "copy.txt").write_text(txt, encoding="utf-8")
# "copy.txt" 新檔名，write_text是文字寫入新文字文檔，txt是文字變數，encoding是指定文字編碼
# 注意: 若檔案與資料夾重命名，則會覆蓋掉該檔案
try:
    with open(output / "log.txt", "a",
              encoding="utf-8") as file:
        file.write("本次整理完成\n")
except OSError as error:
    print("檔案讀寫失敗: ", error)
