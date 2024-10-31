from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from src.schema import *
from tortoise.exceptions import DoesNotExist
import math

site = APIRouter()


@site.get('/', description="获得所有地点")
async def get_sites():
    # 获取所有景点
    sites = await Site.all()

    # 序列化景点数据，选择需要返回的字段
    site_list = [{"id": one_site.id, "name": one_site.name, "city": one_site.city, "description": one_site.description,
                  "picture": one_site.picture, "location": one_site.location, "telephone": one_site.telephone,
                  "time_reference": one_site.time_reference, "transport": one_site.transport, "ticket": one_site.ticket,
                  "open_time": one_site.open_time, "longitude": one_site.longitude, "latitude": one_site.latitude,
                  "reviews": [
                      one_site.review_1,
                      one_site.review_2,
                      one_site.review_3,
                      one_site.review_4,
                      one_site.review_5
                  ]
                  }for one_site in sites]

    return {"sites": site_list}

@site.get('/{site_id}', description="根据site的id获取site的所有信息")
async def get_site_by_id(site_id: int):
    try:
        site = await Site.get(id=site_id)
        site_found = {
            "id": site.id,
            "name": site.name,
            "city": site.city,
            "description": site.description,
            "picture": site.picture,
            "location": site.location,
            "telephone": site.telephone,
            "time_reference": site.time_reference,
            "transport": site.transport,
            "ticket": site.ticket,
            "open_time": site.open_time,
            "longitude": site.longitude,
            "latitude": site.latitude,
            "reviews": [
                site.review_1,
                site.review_2,
                site.review_3,
                site.review_4,
                site.review_5
            ]
        }
        return {"data": site_found}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Site not found")


@site.post('/map', description="获取地图中心附近的景点")
async def map_near(request: MapRequest):
    longitude = request.longitude
    latitude = request.latitude
    scope = request.scope
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

    return {"data": list(sites)}


@site.post('/', description='添加景点')
async def add_site(new_site: SiteSchema):
    # 查看是否已经存在
    site_exist = await Site.get_or_none(name=new_site.name, city=new_site.city)
    if site_exist is not None:
        raise HTTPException(status_code=400, detail="Site with this name in this city already exists.")

    # 插入数据库
    await Site.create(**new_site.dict())
    return {"data": "插入成功"}


@site.post('/user-site', description='用户收藏景点')
async def user_site(user_number: str, site_id: int):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 查找景点是否存在
    site_exist = await Site.get_or_none(id=site_id)
    if site_exist is None:
        raise HTTPException(status_code=400, detail="景点不存在")

    # 添加收藏（无需解包 site_exist）
    await user_exist.sites.add(site_exist)

    return {'data': "收藏成功"}


@site.get('/{user_number}', description='得到用户的收藏列表')
async def user_sites(user_number: str):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number).prefetch_related('sites')
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 获取用户收藏的景点
    sites = await user_exist.sites.all()

    # 构造返回的数据结构
    site_list = [{"id": new_site.id, "name": new_site.name, "city": new_site.city, "location": new_site.location,
                  "picture": new_site.picture, "longitude": new_site.longitude, "latitude": new_site.latitude} for new_site in sites]

    return {"data": site_list}


@site.delete("/user-site", description="用户取消收藏")
async def user_sites(user_number: str, site_id):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 查找景点是否存在
    site_exist = await Site.get_or_none(id=site_id)
    if site_exist is None:
        raise HTTPException(status_code=400, detail="景点不存在")

    # 删除收藏（无需解包 site_exist）
    await user_exist.sites.remove(site_exist)

    return {'data': "取消收藏成功"}



