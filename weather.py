import requests
import json
with open("F-C0032-001.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = requests.get(data)
data_json = data.json()
location = data_json['cwbopendata']['dataset']['location']
for i in location:
    city = i['locationName']
    wx8 = i['weatherElement'][0]['time'][0]['parmeter']['parmenterName']
    maxt8 = i['weatherElement'][1]['time'][0]['parameter']['parameterName']  # 最高溫
    mint8 = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最低溫
    ci8 = i['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
    pop8 = i['weatherElement'][4]['time'][0]['parameter']['parameterName']   # 降雨機率
    print(f'{city}未來 8 小時{wx8}，最高溫 {maxt8} 度，最低溫 {mint8} 度，降雨機率 {pop8} %')