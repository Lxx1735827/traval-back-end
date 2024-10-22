from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.utils.aiutils import *

ai = APIRouter()


@ai.post("/", description="生成对话")
async def create_conversation(number: str, content: str):
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H-%M')
    content = formatted_time + ":::" + "user" + ":::" + content + ";;;"

    exist_user = await User.filter(number=number).first()
    if exist_user is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    new_conversation = await Conversation.create(content=content, user=exist_user)

    return StreamingResponse(completion(content, new_conversation), media_type='text/plain')  # 指定返回内容类型为文本


@ai.get("/{user_id}", description="获取用户历史对话")
async def get_all():
    return {"data": "data"}


@ai.post("/completion", description="完成对话")
async def complete_conversation(number: str, content: str):
    return {"data": "data"}
