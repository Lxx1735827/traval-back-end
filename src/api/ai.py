import math
import json
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.utils.aiutils import *
from src.api.site import map_near

ai = APIRouter()


@ai.post("/", description="生成对话")
async def create_conversation(number: str):
    exist_user = await User.filter(number=number).first()
    if exist_user is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    new_conversation = await Conversation.create(content="", user=exist_user)

    return {"id": new_conversation.id}  # 指定返回内容类型为文本


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

@ai.get("/video/{entity_id}", description="获取视频")
async def get_video(entity_id: int):
    # 获取该用户的所有对话
    video = await Video.filter(entity_id=entity_id).all()

    # 如果对话为空，可以返回一个提示
    if not video:
        return {"data": "static/video/默认视频.mp4"}

    return {"data": video[0].video}


@ai.get("/user/{conversation_id}", description="获取用户指定对话")
async def get_one(conversation_id: int):
    # 获取该用户的所有对话
    conversations = await Conversation.filter(id=conversation_id).all()

    # 如果对话为空，可以返回一个提示
    if not conversations:
        return {"data": [], "message": "没有该对话"}

    conversation_data = {"id": conversations[0].id, "content": conversations[0].content}

    return {"data": conversation_data}


@ai.post("/site", description="景点推荐")
async def site_recommand(longitude: float, latitude: float, scope: int):
    # 获取当前时间
    now = datetime.now()
    # 地球半径，单位为米
    EARTH_RADIUS = 6371000

    # 计算经度和纬度的变化量
    delta_lat = scope / EARTH_RADIUS
    delta_lon = scope / (EARTH_RADIUS * math.cos(math.pi * latitude / 180))

    # 计算经纬度的范围
    min_lat = latitude - (delta_lat * 180 / math.pi)
    max_lat = latitude + (delta_lat * 180 / math.pi)
    min_lon = longitude - (delta_lon * 180 / math.pi)
    max_lon = longitude + (delta_lon * 180 / math.pi)

    # 查询数据库中符合条件的site
    sites = await Site.filter(
        latitude__gte=min_lat,
        latitude__lte=max_lat,
        longitude__gte=min_lon,
        longitude__lte=max_lon
    ).values('id', 'name', 'longitude', 'latitude')

    if not sites:
        raise HTTPException(status_code=404, detail="No sites found in the specified range")

    prompt = f"当前时间为：{now}，请从以下景点推荐一个富含传统文化的景点{list(sites)}, 返回一个数组，第一个元素是景点id,第二个是推荐原因，不输出其他内容"

    content = json.loads(completion2(prompt))
    return {"id": content[0], "reason": content[1]}



@ai.delete("/user/{conversation_id}", description="删除对话")
async def delete_one(conversation_id: int):
    # 获取该对话
    conversation = await Conversation.filter(id=conversation_id).first()

    # 如果对话不存在，返回提示
    if conversation is None:
        return {"data": None, "message": "没有该对话"}

    # 删除对话
    await conversation.delete()

    # 返回确认删除的信息
    return {"data": "对话已删除"}

