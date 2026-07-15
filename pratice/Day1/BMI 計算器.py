# BMI 計算器
print("---BMI 計算器---")
print("請輸入身高(公分):")
h = float(input())
print("請輸入體重(公斤):")
w = float(input())
bmi = w / (h / 100) ** 2
print(f"BMI值為: {bmi:.2f}")

