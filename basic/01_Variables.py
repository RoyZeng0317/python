import sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 01. define variables and print
name = "白𝕽"        # string
age = 20            # integer
height = 178.5      # float
is_student = False  # boolean

info = ["姓名", "年齡", "身高", "是否為學生"]
values = ["白𝕽", 20, 178.5, False]

print("--- 01. 基本宣告與資料型態 --- \n")

for i in range(4):
    print(f"{info[i]}: {values[i]}, 型態: {type(values[i])}")

# 02. (Type Casting)
print("--- 02. 型態轉換 --- \n")
num_str = "100"
num_int = int(num_str)          # string to integer
num_float = float(num_str)      # string to float
back_to_str = str(num_int)      # integer to string

print(f"字串 {num_str!r} 轉整數: {num_int} (型態: {type(num_int)})")
print(f"字串 {num_str!r} 轉浮點數: {num_float} (型態: {type(num_float)})")

# 03. Basic arithmetic operations
print("--- 03. 算術運算 --- \n")
x, y = 10, 3

match o:
    case "+":
        print(f"{x} + {y} = {x + y}")     # addition
    case "-":
        print(f"{x} - {y} = {x - y}")     # subtraction
    case "*":
        print(f"{x} * {y} = {x * y}")     # multiplication
    case "/":
        print(f"{x} / {y} = {x / y}")     # division (result is float)
    case "//":
        print(f"{x} // {y} = {x // y}")   # floor
    case "%":
        print(f"{x} % {y} = {x % y}")     # modulus
    case "**":
        print(f"{x} ** {y} = {x ** y}")   # exponentiation

print("--- 04. f-string formatting --- \n")
pi = 3.141592654
price = 1250
print(f"π 的值是: {pi:.2f}")
print(f"金額加上千分位格式: {price:,} 元")