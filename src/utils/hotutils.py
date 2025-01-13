import time

import requests
from src.utils.aiutils import completion2
from src.accesskey import GAODEKEY
from src.model import Site
import json

def get_hot():
    url = "http://a.sina.cn/s/api/hotTopic/search?from=wap&plat=travel&sort=hot"

    # 设置 User-Agent 和 Cookie
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
    }

    # 发送 GET 请求
    data = requests.get(url=url, headers=headers)
    data = data.json()['data']['list']
    dates = []
    index = 0
    que = "从以下景点中选出3个热点包含地点，景点，不要国外的"
    for record in data:
        dates.append({
            "id": index,
            "title": record['title'],
            "url": record["wap_url"]
        })
        que += f"{index}:{record['title']}"
    que += "。只给出一个数字id，不返回其他，数字id之间用英文逗号隔开"
    answer = completion2(que).split(',')
    titles = []
    for i in range(0, len(answer)):
        titles.append(dates[int(answer[i])]["title"])
    return titles


def get_sites(content):
    que: str = "根据这个标题:"+content + """，推荐8个相关景点，只返回景点中文，用英文逗号隔开"""
    return completion2(que).split(',')


def get_info(content):
    que: str = "根据这个景点:"+content + """
    ，提取城市，景点，并给出描述。回答格式为一个字典如下：
    {”城市“: ”“, "景点": "", "描述": ""}
    只返回字典格式，不输出其他类容
    """
    time.sleep(1)
    return json.loads(completion2(que))["城市"], json.loads(completion2(que))["景点"], json.loads(completion2(que))["描述"]


def get_location(site, city):
    url = "https://restapi.amap.com/v3/assistant/inputtips"
    params = {
        "key": GAODEKEY,
        "keywords": city+site
    }
    response = requests.get(url=url, params=params)
    print(site)
    print(response.json())
    location = response.json()['tips'][0]['district']
    longitude = response.json()['tips'][0]['location'].split(',')[0]
    latitude = response.json()['tips'][0]['location'].split(',')[1]

    return location, longitude, latitude



if __name__ == "__main__":
    # print(get_hot())
    # print(get_sites("起猛了南京居然有冰雪大世界"))
    # data = get_info("玄武湖公园")
    # print(json.loads(get_info("起猛了南京居然有冰雪大世界")))
    print(get_location("玄武湖公园", "南京"))







