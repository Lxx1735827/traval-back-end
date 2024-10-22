import requests
import json

from datetime import datetime

from src.setting import *
from src.model import *


async def completion(content: str, conversation: Conversation):
    # 构造请求数据
    data = {
        "assistant_id": "lWdLGdyOUqWl",
        "user_id": USERID,
        "stream": True,  # 确保启用流式输出
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": content
                    }
                ]
            }
        ]
    }

    # 发送 POST 请求，使用 stream=True
    response = requests.post(URL, headers=HEADERS, data=json.dumps(data), stream=True)
    contents = ""
    if response.status_code == 200:
        # 流式处理响应内容
        for line in response.iter_lines():
            if line:  # 忽略空行
                line_str = line.decode('utf-8')  # 解码为字符串
                if line_str.startswith('data: '):
                    json_line_str = line_str[len('data: '):]  # 移除 'data: ' 前缀
                    if json_line_str != '[DONE]':
                        json_line = json.loads(json_line_str)  # 解析 JSON
                        # 检查并输出助手内容
                        content = json_line.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if content:
                            contents += content
                            yield content  # 使用 yield 返回内容
        now = datetime.now()
        formatted_time = now.strftime('%Y-%m-%d %H-%M')
        contents = formatted_time + ":::" + "system" + ":::" + contents + ";;;"
        conversation.content += contents
        await conversation.save()
    else:
        yield f"Error: {response.status_code}, {response.text}"


if __name__ == "__main__":
    completion("你是谁")
