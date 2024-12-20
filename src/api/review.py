from fastapi import APIRouter, File, UploadFile, HTTPException
from src.schema import *
from tortoise.exceptions import DoesNotExist

review = APIRouter()


@review.get('/all', description="获得所有评论")
async def get_reviews():
    # 获取所有评论
    reviews = await Review.all()

    # 序列化评论数据，选择需要返回的字段
    review_list = [
        {
            "id": review.id,
            "entity_id": review.entity_id,
            "entity_type": review.entity_type,
            "user_id": review.user_id,
            "content": review.content,
            "created_at": review.created_at.isoformat()  # 将日期时间转换为字符串
        }
        for review in reviews
    ]

    return {"reviews": review_list}


@review.get('/{review_id}', description="根据review的id获取review的所有信息")
async def get_review_by_id(review_id: int):
    try:
        review = await Review.get(id=review_id)
        review_found = {
            "id": review.id,
            "entity_id": review.entity_id,
            "entity_type": review.entity_type,
            "user_id": review.user_id,
            "content": review.content,
            "created_at": review.created_at.isoformat()  # 将日期时间转换为字符串
        }
        return {"data": review_found}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Review not found")


@review.get('/site/{site_id}', description="根据site的id获取reviews")
async def get_review_of_site(site_id: int):
    site = await Site.get(id=site_id)

    # 获取与指定 site_id 相关的所有评论
    reviews = await Review.filter(entity_id=site_id, entity_type="景点").all()

    # 序列化评论数据，选择需要返回的字段
    review_list = [
        {
            "id": review.id,
            "entity_id": review.entity_id,
            "entity_type": review.entity_type,
            "user_id": review.user_id,
            "content": review.content,
            "created_at": review.created_at.isoformat()  # 将日期时间转换为字符串
        }
        for review in reviews
    ]

    return {
        "object": {
            "type": "site",
            "id": site.id,
            "name": site.name,
            "city": site.city
        },
        "reviews": review_list
    }


@review.get('/restaurant/{restaurant_id}', description="根据restaurant的id获取reviews")
async def get_review_of_restaurant(restaurant_id: int):
    # 获取指定的餐厅信息
    restaurant = await Restaurant.get(id=restaurant_id)

    # 获取与指定 restaurant_id 相关的所有评论
    reviews = await Review.filter(entity_id=restaurant_id, entity_type="餐厅").all()

    # 序列化评论数据，选择需要返回的字段
    review_list = [
        {
            "id": review.id,
            "entity_id": review.entity_id,
            "entity_type": review.entity_type,
            "user_id": review.user_id,
            "content": review.content,
            "created_at": review.created_at.isoformat()  # 将日期时间转换为字符串
        }
        for review in reviews
    ]

    return {
        "object": {
            "type": "restaurant",
            "id": restaurant.id,
            "name": restaurant.name,
            "city": restaurant.city
        },
        "reviews": review_list
    }


@review.get('/user/{user_id}', description="根据user的id获取reviews")
async def get_review_of_user(user_id: int):
    # 获取与指定 user_id 相关的所有评论
    reviews = await Review.filter(user_id=user_id).all()

    # 序列化评论数据，选择需要返回的字段
    review_list = [
        {
            "id": review.id,
            "entity_id": review.entity_id,
            "entity_type": review.entity_type,
            "user_id": review.user_id,
            "content": review.content,
            "created_at": review.created_at.isoformat()  # 将日期时间转换为字符串
        }
        for review in reviews
    ]

    return {
        "object": {
            "type": "user",
            "id": user_id,
        },
        "reviews": review_list
    }
