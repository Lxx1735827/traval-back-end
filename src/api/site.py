from fastapi import APIRouter, HTTPException
from src.schema import *

site = APIRouter()


@site.get('/', description="获得所有地点")
async def get_sites():
    # 获取所有景点
    sites = await Site.all()

    # 序列化景点数据，选择需要返回的字段
    site_list = [{"id": one_site.id, "name": one_site.name, "city": one_site.city, "description": one_site.description,
                  "picture": one_site.picture, "location": one_site.location, "longitude": one_site.longitude,
                  "latitude": one_site.latitude} for one_site in sites]

    return {"sites": site_list}


@site.post('/', description='添加景点')
async def add_site(new_site: SiteSchema):
    # 查看是否已经存在
    site_exist = await Site.get_or_none(name=new_site.name)
    if site_exist is not None:
        raise HTTPException(status_code=400, detail="Site with this name already exists.")

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



