import math
import os
import aiofiles
import re

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import List

from src.utils.aiutils import *
from src.utils.aiutils2 import *
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
    content = formatted_time + ":::" + "user" + ":::" + f"[{content}]" + ";;;"  # 构造用户输入的记录格式

    # 查找现有对话记录
    conversation = await Conversation.filter(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="该对话不存在")

    # 更新对话内容，添加用户的输入
    conversation.content += content
    await conversation.save()

    return StreamingResponse(completion(conversation.content, conversation), media_type='text/plain')
@ai.post("/completion/image", description="完成包含图片的对话")
async def complete_conversation(conversation_id: int, picture: UploadFile = File(), content: str = "这张图片讲了什么",):
    # 格式化当前时间
    now = datetime.now()
    formatted_time = now.strftime('%Y-%m-%d %H:%M')
    safe_file_name = re.sub(r'[<>:"/\\|?*]', '_', formatted_time)

    save_directory = "static/conversation"  # 存放头像文件的目录
    file_extension = os.path.splitext(picture.filename)[1]  # 获取文件的扩展名
    save_path = save_directory + f"/{safe_file_name}{file_extension}"
    async with aiofiles.open(save_path, "wb") as buffer:
        await buffer.write(await picture.read())
    content = formatted_time + ":::" + "user" + ":::" + f"[{content}]" +f"[{save_path}]"+ ";;;"

    # 查找现有对话记录
    conversation = await Conversation.filter(id=conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="该对话不存在")

    # 更新对话内容，添加用户的输入
    conversation.content += content
    await conversation.save()
    return StreamingResponse(send_request(save_path, conversation.content, conversation), media_type='text/plain')

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

    prompt = f"当前时间为：{now}，请从以下景点推荐一个富含传统文化的景点{list(sites)}, 只返回景点id"

    content = (int)(completion2(prompt))
    site = await Site.get_or_none(
        id=content
    )

    if site is None:
        raise HTTPException(status_code=404, detail="错误")

    contents = completion2("给出推荐传统景点为这个景点的原因" + site.name + site.description + site.city)

    data = {"id": content, "reason": contents}
    return {"data": data}



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

@ai.post("/route-recommend", description="路径规划之AI推荐")
async def route_recommend(city: str, days: int, tag: str):
    # 查询包含 city 的前50个景点
    cities = await Site.filter(location__icontains=city)[:30]

    if not cities:
        raise HTTPException(status_code=401, detail="没有这个城市")
    try:
        # 处理获取到的景点数据
        data = [[city.id, city.name] for city in cities]
        answer = str(data) + "在以上的景点当中推荐10个符合下面标签的景点，标签为：" + tag + ",返回只id，用英文逗号隔开"

        # 模拟外部推荐系统返回的推荐景点id（这里使用 completion2 生成推荐列表）
        recommended_ids = completion2(answer).split(',')

        # 将返回的推荐id转换为整数列表
        recommended_ids = [int(recommended_id.strip()) for recommended_id in recommended_ids]

        # 根据推荐的id查询符合条件的景点
        recommended_cities = await Site.filter(id__in=recommended_ids)[:15]

        # 返回推荐景点的id列表
        return {"city_data": [[city.id, city.name, city.picture, city.location, city.latitude, city.longitude, city.description] for city in recommended_cities],
                "days": days}
    except:
        return {"city_data": [[city.id, city.name, city.picture, city.location, city.latitude, city.longitude, city.description] for city in cities[:15]],
                "days": days}