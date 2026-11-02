import re
txt = "我想被 _ziejie 幹 99 次"
num = re.findall(r"\d+", txt)
print(num)