import numpy as np
# 基本對象：建立陣列的幾種寫法
a = np.array([1, 2, 3]) # 基本的 list -> 一維陣列 [1 2 3]
b = np.array([[1, 2], [3, 4]])  # 二為數列 -> 二維陣列(矩陣) [[1 2] [3 4]]
c = np.array([1, 2, 3, 4, 5], ndmin= 2) # 最小維度：ndmin=2 強制把一維資料包成二維 -> [[1 2 3 4 5]]
d = np.array([1, 2, 3], dtype = complex)    # dtype 參數：指定元素型態為複數 -> [1.+0.j 2.+0.j 3.+0.j]
print(a, b, c, d)

# dt = np.dtype(np.int32)     # 使用標量類型：指定 32 位元整數
# int8, int16, int32, int64 -> 4 types of data can use this string 'i1', 'i2', 'i4', 'i8' to replace
# dt = np.dtype('i4')     # 用字串代碼 'i4' 等同 np.int32
# dt = np.dtype('<i4')    # bit 順帶標註：'<' 代表小端序(byte 順序)
# dt = np.dtype([('age', np.int8)])   # 首先建立結構化數據模型：定義一個只有 age 欄位的結構
# print(dt)
# a = np.array([(10,), (20,), (30,),], dtype = dt)   # 用上面的結構建立資料
# print(a)

# 結構化陣列(structured array)：像資料庫表格一樣，每筆資料有多個具名欄位
# name: 'S20' 字串(最長20字元)、age: 'i1' 1 byte 整數、marks: 'f4' 4 byte 浮點數
student = np.dtype([('name', 'S20'), ('age', 'i1'), ('marks', 'f4')])
# print(student)
a = np.array([('abc', 21, 50), ('xyz', 18, 75)], dtype = student)  # 建立兩筆學生資料(name, age, marks)
print(a)  # 結果: [(b'abc', 21, 50.) (b'xyz', 18, 75.)]，b'...' 是因為字串以 bytes 儲存
