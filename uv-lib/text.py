import re

txt = "這個留言有 12 個讚"
match = re.search(r"\d+", txt)  # 查找匹配，匹配規則，待查找的文字
# r 是指原始字串 \d 表示一個數字 + 則是一次或多次
# 全部加起來就是匹配連續的數字
if match:
    print(match.group())
print(re.sub(r"\d+", "很多", txt))  # 匹配規則，替換文字，原始字串；根據規則替換
txt.replace("12", "很多")   # 根據指定字串進行替換