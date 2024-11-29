import json
import base64
import hmac
import asyncio
from urllib.parse import urlparse
import hashlib
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
from urllib.parse import urlencode
import websocket
from src.setting import *
from src.model import *

appid = "bf8a04ba"    #填写控制台中获取的 APPID 信息
APISecret = "MzZlNzY3ZTc1N2YxZWIxNzQ5MmQ2N2Zi"
APIKey = "4ed5cad270cf3f40e71ee1b2d0f2b9f6"
imageunderstanding_url = "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image"#云端环境的服务地址

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, imageunderstanding_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(imageunderstanding_url).netloc
        self.path = urlparse(imageunderstanding_url).path
        self.ImageUnderstanding_url = imageunderstanding_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }

        # 拼接鉴权参数，生成url
        url = self.ImageUnderstanding_url + '?' + urlencode(v)
        return url


# 读取图像并转换为 base64 编码
def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# 构建请求数据
def build_payload(image_base64, question):
    payload = {
        "header": {
            "app_id": "bf8a04ba",
        },
        "parameter": {
            "chat": {
                "domain": "general",
                "temperature": 0.5,
                "top_k": 4,
                "max_tokens": 8000,
                "auditing": "default"
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "user",
                        "content": image_base64,
                        "content_type": "image"
                    },
                    {
                        "role": "user",
                        "content": question,
                        "content_type": "text"
                    }
                ]
            }
        }
    }
    return json.dumps(payload)


async def send_request(image_path, question, conversation: Conversation):
    # 获取图像的 base64 编码
    image_base64 = image_to_base64(image_path)
    payload = build_payload(image_base64, question)

    wsParam = Ws_Param(appid, APIKey, APISecret, imageunderstanding_url)
    ws = websocket.create_connection(wsParam.create_url())

    # 发送数据
    ws.send(payload)
    contents = ""
    # 流式接收响应
    while True:
        response = ws.recv()
        if response:  # 如果有响应
            content = json.loads(response)["payload"]["choices"]["text"][0]["content"]
            contents += content
            yield content
        else:
            break  # 如果没有响应，退出循环
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H-%M')
    contents = formatted_time + ":::" + "system" + ":::" + contents + ";;;"
    conversation.content += contents
    await conversation.save()
    # 关闭连接
    ws.close()
# 主函数
async def main():
    image_path = "图片1.png"  # 替换为你的图像文件路径
    question = "这张图片讲了什么"  # 提问内容
    await send_request(image_path, question)

if __name__ == "__main__":
    # 使用 asyncio 事件循环运行主函数
    asyncio.run(main())