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


@ai.get("/{user_number}", description="获取用户历史对话")
async def get_all(user_number: str):
    exist_user = await User.filter(number=user_number).first()
    if exist_user is None:
        raise HTTPException(status_code=404, detail="该用户不存在")
        # 获取该用户的所有对话
    conversations = await Conversation.filter(user=exist_user).all()

    # 如果对话为空，可以返回一个提示
    if not conversations:
        return {"data": [], "message": "该用户没有历史对话"}

    conversation_data = [
        {"id": conversation.id, "content": conversation.content}
        for conversation in conversations
    ]
    return {"data": conversation_data}


@ai.post("/completion", description="完成对话")
async def complete_conversation(content: str, conversation_id: int):
    # 格式化当前时间
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    content = formatted_time + ":::" + "user" + ":::" + content + ";;;"  # 构造用户输入的记录格式

    # 查找现有对话记录
    conversation = await Conversation.filter(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="该对话不存在")

    # 更新对话内容，添加用户的输入
    conversation.content += content
    await conversation.save()

    return StreamingResponse(completion(conversation.content, conversation), media_type='text/plain')
