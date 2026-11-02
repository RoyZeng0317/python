# 先執行: uv init(如果沒有出現: pyproject.toml)
# 再執行: uv add python-dotenv(如果出現錯誤則使用 pip install python-dotenv)
import os
from dotenv import load_dotenv
# import dotenv
print(os.getenv("HOME"))

load_dotenv()

os.getenv("COMMENT_API_URL", "https://dummyjson.com")
# 按照: comment_api_url 進行讀取
# 第二變數為默認值，若找不到即可使用此網址