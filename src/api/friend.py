import os
import re
import aiofiles
from fastapi import APIRouter, HTTPException
from tortoise.expressions import Q
from fastapi import File, UploadFile
from datetime import datetime
from typing import Dict

from src.schema import FriendConversationSchema
from src.model import FriendConversation, User

friend = APIRouter()


@friend.post("/send-message", description="发送信息")
async def send_message(message: FriendConversationSchema):
    user2 = await User.get_or_none(number=message.user_id2)
    if user2 is None:
        raise HTTPException(status_code=404, detail="好友不存在")
    await FriendConversation.create(**message.dict())
    return {"data": "发送成功"}


@friend.post('/send-message/picture', description="发送携带图片的信息")
async def send_message_picture(user_id1: str, user_id2: str, content: str, create_time: str, file: UploadFile = File(...)):
    user2 = await User.get_or_none(number=user_id2)
    if user2 is None:
        raise HTTPException(status_code=404, detail="好友不存在")
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', formatted_time)

    save_directory = "static/conversation"  # 存放头像文件的目录
    file_extension = os.path.splitext(file.filename)[1]  # 获取文件的扩展名
    save_path = save_directory + f"/{safe_file_name}{file_extension}"
    async with aiofiles.open("src/" + save_path, "wb") as buffer:
        await buffer.write(await file.read())
    content = f"##[{save_path}]" + content
    message = {
        "user_id1": user_id1,
        "user_id2": user_id2,
        "content": content,
        "state": 0,
        "create_time": create_time
    }
    await FriendConversation.create(**message)
    return {"data": "发送成功"}


@friend.get("/history-message", description="获得历史对话")
async def history_message(user_id1: str, user_id2: str):
    """

    :param user_id1: 自己
    :param user_id2: 对方
    :return:
    """
    contents = await FriendConversation.filter((Q(user_id1=user_id1) & Q(user_id2=user_id2)) | (Q(user_id1=user_id2) & Q(user_id2=user_id1))).all()
    # 遍历查询结果
    message_data = []
    for conversation in contents:
        # 将每条对话的内容提取为字典
        message_data.append({
            "user_id1": conversation.user_id1,
            "user_id2": conversation.user_id2,
            "content": conversation.content,
            "create_time": conversation.create_time
        })
        if conversation.user_id1 == user_id2:
            if conversation.state == 0:
                conversation.state = 1
                await conversation.save()

    return {"data": message_data}


@friend.get("/new-message", description="获得未读消息")
async def new_message(user_id1: str, user_id2: str):
    """

    :param user_id1:自己
    :param user_id2:好友
    :return:
    """
    contents = await FriendConversation.filter((Q(user_id1=user_id2) & Q(user_id2=user_id1)) & Q(state=0)).all()
    message_data = []
    for conversation in contents:
        message_data.append({
            "user_id1": conversation.user_id1,
            "user_id2": conversation.user_id2,
            "content": conversation.content,
            "create_time": conversation.create_time
        })
        conversation.state = 1
        await conversation.save()
    return {"data": message_data}
