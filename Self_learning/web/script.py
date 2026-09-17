# pyright: reportMissingImports=false, reportOptionalMemberAccess=false, reportAttributeAccessIssue=false
from pyscript import document

# 操控 HTML 元素
user_box = document.querySelector("#user-display")
user_box.innerHTML = "Python 成功載入! 使用者資料: admin"

# 定義按鈕點擊事件
def hanle_back(event):
    user_box.innerText = "點擊了返回按鈕!"

# 綁定事件到按鈕上
back_btn = document.querySelector("#back-btn")
back_btn.onclick = hanle_back