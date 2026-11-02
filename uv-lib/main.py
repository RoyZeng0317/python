# uv lib install
# uv 庫安裝
# powershell (win):
# powershell -ExecutionPolicy ByPass -c "irm https://uv.agentsmirror.com/install-cn.ps1 | iex"
# terminal (Mac/Linux/CMD):
# curl -LsSf https://uv.agentsmirror.com/install-cn.sh | sh
# 安裝完畢後 (When install finished)
# 按下 ctrl+shift+P 輸入: clear cache and reload window
# press the ctrl+shift+P enter: clear che and reload window
# 執行指令 (run the code):
# uv init
# 使用 requests 庫 (use the requests lib):
# uv add requests
import requests

print("請求庫已經可以正常導入了")
# 測試 (test): uv run main.py
# 不能使用 (don't use): python main.py
# 或者 (or): 
# Mac/Linux/CMD: source .venv/bin/activate
# powershell: .venv\Scripts\activate
# 再執行: (then run): python main.py
# 別人做好的: cd uv-lib
# uv sync
# uv run main.py
