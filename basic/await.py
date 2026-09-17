import asyncio

async def fetch_data():
    print("開始抓資料...")
    await asyncio.sleep(2)  # 等待兩秒，用意是模擬 I/O 等待
    print("資料抓完了")
    return {"data": 123}

async def main():
    result = await fetch_data() # 等待 fetch_data 執行完成
    print(result)

asyncio.run(main())

