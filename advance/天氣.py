import requests, time

def forecast(address):
    # 將主要縣市個別的 JSON 代碼列出
    api_list = {"宜蘭縣": "F-D0047-001", "桃園市": "F-D0047-005", "新竹縣": "F-D0047-009", "苗栗縣": "F-D-0047-013",
                "彰化縣": "F-D0047-017", "南投縣": "F-D0047-021", "雲林縣": "F-D0047-025", "嘉義縣": "F-D-0047-029",
                "屏東縣":"F-D0047-033","臺東縣":"F-D0047-037","花蓮縣":"F-D0047-041","澎湖縣":"F-D0047-045",
                "基隆市":"F-D0047-049","新竹市":"F-D0047-053","嘉義市":"F-D0047-057","臺北市":"F-D0047-061",
                "高雄市":"F-D0047-065","新北市":"F-D0047-069","臺中市":"F-D0047-073","臺南市":"F-D0047-077",
                "連江縣":"F-D0047-081","金門縣":"F-D0047-085"}
    for name in api_list:
        if name in address:
            city_id = api_list[name] # 根據提供地址，取得縣市代碼
    result = {}
    code = '你的氣象 token'
    t = time.time()
    t1 = time.localtime( t + 28800)             # 因為 colab 所在時區，要額外增加八小時 28800 秒
    t2 = time.localtime( t + 28800 + 10800)     # 因為 colab 所在時區，要額外增加八小時 28800 秒與三小時 10800 秒
    now = time.strftime('%Y-%m-%dT%H:%M:%S', t1)
    now2 = time.strftime('%Y-%m-%dT%H:%M:%S', t2)
    url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{city_id}?Authorization={code}&elementName=WeatherDescription&timeFrom={now}&timeTo={now2}'
    req = requests.get(url) # 取得主要縣市預報資料
    data  = req.json()      # json 格式化訊息內容
    location = data['records']['locations'][0]['location']
    city = data['records']['locations'][0]['locationName']
    for i in location:
        area = i['locationName']
        note = i['weatherElement0'][0]['time'][0]['elementValue'][0]['value']
    return result

print(forecast('雲林縣虎尾鎮興南里147號'))