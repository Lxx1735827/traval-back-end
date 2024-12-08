from fastapi import APIRouter, File, UploadFile, HTTPException
from src.schema import *
from tortoise.exceptions import DoesNotExist
import math
import random
import time
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from scipy.linalg import norm
import re
import regex
from tortoise import Tortoise
from src.setting import SITE
# LLM调用
from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'f5f377c0'
SPARKAI_API_SECRET = 'YjFiNWZmYTQwMGMyZDZhOGIwMzk0NDYw'
SPARKAI_API_KEY = '3d7cdb75e47c594d01a98d691b950aa2'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

site = APIRouter()


@site.get('/', description="获得所有地点")
async def get_sites():
    # 获取所有景点
    sites = await Site.all()

    # 序列化景点数据，选择需要返回的字段
    site_list = [{"id": one_site.id, "name": one_site.name, "city": one_site.city, "description": one_site.description,
                  "picture": one_site.picture, "location": one_site.location, "telephone": one_site.telephone,
                  "time_reference": one_site.time_reference, "transport": one_site.transport, "ticket": one_site.ticket,
                  "open_time": one_site.open_time, "longitude": one_site.longitude, "latitude": one_site.latitude
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
            "latitude": site.latitude
        }
        return {"data": site_found}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Site not found")


@site.post('/map', description="获取地图中心附近的景点")
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

    # 查询数据库中符合条件的site
    sites = await Site.filter(
        latitude__gte=min_lat,
        latitude__lte=max_lat,
        longitude__gte=min_lon,
        longitude__lte=max_lon
    ).values('id', 'name', 'longitude', 'latitude', 'picture', 'location')

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


@site.get('/user/{user_number}', description='得到用户的收藏列表')
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

@site.get("/search/{key}", description="搜索景点名字，返回最相似的7个")
async def search_site(key: str):
    try:
        key_parts = list(key)
        regex_pattern = ".*" + ".*".join(map(re.escape, key_parts)) + ".*"
        conn = Tortoise.get_connection("default")
        sites = await conn.execute_query('SELECT * FROM site WHERE name REGEXP %s', regex_pattern)
        print(sites)
        # site = await Site.filter(name__posix_regex=regex_pattern)#.limit(7)  # 使用first()取最匹配的记录
        if not sites:
            raise HTTPException(status_code=404, detail="Site not found")
        real_sites = sites[1]
        # filtered_sites = [site for site in real_sites if site['description'] != '暂无介绍']
        result = [{"id": site["id"], "name": site["name"], "location": site["location"],  "picture": site["picture"]} for site in real_sites[:7]]

        return {"data": result}

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Site not found")

@site.get("/largesearch/{key}", description="搜索景点名字，返回最相似的")
async def search_site_large(key: str):
    try:
        keywords = semantic_split(key)
        if not isinstance(keywords,list):
            result = await search_site(key)
            return result
        else:
            rough = []
            for keyword in keywords:
                temp = await Site.filter(name__icontains=keyword)
                rough.extend(temp)
            unique_rough = list({site.id: site for site in rough}.values())

            similarities = [(site, tf_similarity(site.name, key)) for site in unique_rough]

            # 按相似度从大到小排序
            sorted_sites = [{"id":site.id, "name": site.name, "picture": site.picture, "location": site.location} for site, _ in sorted(similarities, key=lambda x: x[1], reverse=True)]

            # 限制返回最多35个site
            return {"data": sorted_sites[:35]}

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Site not found")

def semantic_split(key: str):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [
        ChatMessage(role="system",
                    content="你是一个语义分析助手，专注于将中文短语拆分成有意义的最小单元，保留核心名词，并尽可能涵盖上下层次的含义。"),
        ChatMessage(
            role="user",
            content=f"将搜索词'{key}'拆分成有意义的最小单元，保留核心名词或短语，并尽量涵盖整体及子层次的含义。"
                    f"(必须严格按照此格式输出)输出格式为：'keywords: xxx, xxx, xxx'。例如："
                    f"1. 'keywords: 成都, 熊猫, 基地'"
                    f"2. 'keywords: 四川大学, 江安校区, 四川, 大学, 江安'"
        )
    ]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    text = a.generations[0][0].text.strip("'")  # 从数据中提取文本
    print(text)
    pattern = r'^\s*keywords:\s*([\p{L}\d_]+(?:\s*,\s*[\p{L}\d_]+)*)\s*$'
    if regex.match(pattern, text):
        keywords = text.replace('keywords:', '').strip()
        print(f"Yes!Keywords:{keywords}")
        result = [item.strip() for item in keywords.split(',')]
    else:
        print(f"No~Key:{key}")
        result = key
    return result

@site.get('/user/recommend/{user_number}', description='推荐算法')
async def user_recommend_sites(user_number: str):
    # 查找用户是否存在
    user_exist = await User.get_or_none(number=user_number).prefetch_related('sites')
    if user_exist is None:
        raise HTTPException(status_code=400, detail="用户不存在")
    sites = await user_exist.sites.all()
    site_ids1 = [site_it.id for site_it in sites]
    sites = await user_exist.sites.all()
    site_ids2 = [site_it.id for site_it in sites]
    sites = list(set(site_ids1).union(set(site_ids2)))
    random.seed(time.time())
    random.shuffle(sites)
    site_lists = set()
    for site_id in sites:
        return_sites = await SiteRelationship.filter(site_from_ids__icontains=site_id).values("site_to_ids")
        for return_site in return_sites:
            site_list = return_site["site_to_ids"].split("*")[:-1]
            site_list = set(site_list)
            site_lists = site_lists.union(site_list)
            if len(site_lists) > 7:
                break
    for i in range(len(site_lists) - 1, 7):
        site_lists.add(SITE[i])
    site_lists = [int(site_) for site_ in site_lists]
    site_lists = await Site.filter(id__in=site_lists)
    site_list = [{"id": new_site.id, "name": new_site.name,
                  "picture": new_site.picture, "location": new_site.location} for
                 new_site in site_lists]

    return {"data": site_list}

def tf_similarity(s1, s2):
    def add_space(s):
        return ' '.join(list(s))

    s1, s2 = add_space(s1), add_space(s2) #在字中间加上空格
    cv = CountVectorizer(tokenizer=lambda s: s.split()) #转化为TF矩阵
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray() #计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))

