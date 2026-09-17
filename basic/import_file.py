# plan 1
"""
import 基本電學

V = 基本電學.I * 基本電學.R
"""
# plan 2
"""
from 基本電學 import I, R

V = I * R
print(f"驗算電壓 -> {V}")
"""
# plan 3
def calc_r(V, I):
    return V / I
if __name__