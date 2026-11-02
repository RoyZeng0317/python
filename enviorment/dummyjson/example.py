import requests

url = "https://dummyjson.com/comments"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    print("收到留言: ", len(data["comments"]))
    # 請求超時報錯
except requests.exceptions.Timeout as error:
    print("請求超時，請檢查網路或稍後再試: ", error)
    # JSON 解析報錯
except requests.exceptions.JSONDecodeError as error:
    print("JSON 解析失敗: ", error)
    print("接口返回原始內容: ", response.text)