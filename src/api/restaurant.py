from fastapi import APIRouter, HTTPException
from src.schema import *
from tortoise.exceptions import DoesNotExist
import math

restaurant = APIRouter()

@restaurant.get('/', description="获得所有餐厅")
async def get_restaurants():
    # 获取所有餐厅
    restaurants = await Restaurant.all()

    # 序列化餐厅数据，选择需要返回的字段
    restaurant_list = [{
        "id": one_restaurant.id,
        "name": one_restaurant.name,
        "city": one_restaurant.city,
        "image": one_restaurant.image,
        "location": one_restaurant.location,
        "telephone": one_restaurant.telephone,
        "longitude": one_restaurant.longitude,
        "latitude": one_restaurant.latitude,
        "reviews": [
            one_restaurant.review_1,
            one_restaurant.review_2,
            one_restaurant.review_3,
            one_restaurant.review_4,
            one_restaurant.review_5
        ]
    } for one_restaurant in restaurants]

    return {"restaurants": restaurant_list}

@restaurant.get('/{restaurant_id}', description="根据restaurant的id获取restaurant的所有信息")
async def get_restaurant_by_id(restaurant_id: int):
    try:
        restaurant = await Restaurant.get(id=restaurant_id)
        restaurant_found = {
            "id": restaurant.id,
            "name": restaurant.name,
            "city": restaurant.city,
            "image": restaurant.image,
            "location": restaurant.location,
            "telephone": restaurant.telephone,
            "longitude": restaurant.longitude,
            "latitude": restaurant.latitude,
            "reviews": [
                restaurant.review_1,
                restaurant.review_2,
                restaurant.review_3,
                restaurant.review_4,
                restaurant.review_5
            ]
        }
        return {"data": restaurant_found}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Restaurant not found")

@restaurant.post('/map', description="获取地图中心附近的餐厅")
async def map_near(longitude: float, latitude: float, scope: int):
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

    # 查询数据库中符合条件的restaurant
    restaurants = await Restaurant.filter(
        latitude__gte=min_lat,
        latitude__lte=max_lat,
        longitude__gte=min_lon,
        longitude__lte=max_lon
    ).values('id', 'name', 'longitude', 'latitude')

    if not restaurants:
        raise HTTPException(status_code=404, detail="No restaurants found in the specified range")

    return {"data": list(restaurants)}

@restaurant.post('/', description='添加餐厅')
async def add_restaurant(new_restaurant: RestaurantSchema):
    # 查看是否已经存在
    restaurant_exist = await Restaurant.get_or_none(name=new_restaurant.name, city=new_restaurant.city)
    if restaurant_exist is not None:
        raise HTTPException(status_code=400, detail="Restaurant with this name in this city already exists.")

    # 插入数据库
    await Restaurant.create(**new_restaurant.dict())
    return {"data": "插入成功"}

@restaurant.post('/user-restaurant', description='用户收藏餐厅')
async def user_restaurant(user_number: str, restaurant_id: int):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 查找餐厅是否存在
    restaurant_exist = await Restaurant.get_or_none(id=restaurant_id)
    if restaurant_exist is None:
        raise HTTPException(status_code=400, detail="餐厅不存在")

    # 添加收藏（无需解包 restaurant_exist）
    await user_exist.restaurants.add(restaurant_exist)

    return {'data': "收藏成功"}

@restaurant.get('/{user_number}', description='得到用户的收藏列表')
async def user_restaurants(user_number: str):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number).prefetch_related('restaurants')
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 获取用户收藏的餐厅
    restaurants = await user_exist.restaurants.all()

    # 构造返回的数据结构
    restaurant_list = [{
        "id": new_restaurant.id,
        "name": new_restaurant.name,
        "city": new_restaurant.city,
        "location": new_restaurant.location,
        "image": new_restaurant.image,
        "longitude": new_restaurant.longitude,
        "latitude": new_restaurant.latitude
    } for new_restaurant in restaurants]

    return {"data": restaurant_list}

@restaurant.delete("/user-restaurant", description="用户取消收藏")
async def user_restaurant_remove(user_number: str, restaurant_id: int):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")

    # 查找餐厅是否存在
    restaurant_exist = await Restaurant.get_or_none(id=restaurant_id)
    if restaurant_exist is None:
        raise HTTPException(status_code=400, detail="餐厅不存在")

    # 删除收藏（无需解包 restaurant_exist）
    await user_exist.restaurants.remove(restaurant_exist)

    return {'data': "取消收藏成功"}
