import os
# 指定開啟 note.txt 檔案
fp = open("note.txt", "w")
# 檔案路徑
fp.write("\n薯先森是我的男朋友\n")
print("已經將內容寫入檔案內")

if fp != None:
    print("檔案開啟成功!")
else:
    print("檔案開啟失敗")
fp.close()
