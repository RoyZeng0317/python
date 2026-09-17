import asyncio, time

async def fetch_data(name, delay):
    print(f"Start to fetch{name}")
    await asyncio.sleep(delay)  # 模擬等待網路回應
    print(f"{name} Finished to fetch")
    return f"Result: {name}"    # 回傳結果值

async def main():
    start = time.perf_counter()

    # 依序執行(總共約需 3 秒)
    # r1 = await fetch_data("A", 1)
    # r2 = await fetch_data("B", 2)

    # 同時執行(共約需 2 秒，因兩者並行等待)
    results = await asyncio.gather(
        fetch_data("A", 2),
        fetch_data("B", 2),
    )

    print(results)
    print(f"耗時: {time.perf_counter() - start:.2f} 秒")    # .2f 是浮點數函數，顯示小數點後兩位

asyncio.run(main())
