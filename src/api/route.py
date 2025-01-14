from fastapi import APIRouter, UploadFile, File, Body
from src.schema import *
from src.utils.pictureutils import day_routes
from src.utils.routeutils import *
from datetime import datetime
import json
import os

route = APIRouter()


@route.post("/", description="生成规划")
async def create_routes(routes: List[DayRouteSchema]):
    days = []
    ids = []
    for route_ in routes:
        id_ = [0]
        day = {
            route_.start_point.name: {
                "latitude": route_.start_point.latitude,
                "longitude": route_.start_point.longitude
            }
        }
        for site in route_.sites:
            day[site.name] = {"latitude": site.latitude,  "longitude": site.longitude}
            id_.append(site.id)
        day[route_.end_point.name] = {"latitude": route_.end_point.latitude, "longitude": route_.end_point.longitude}
        id_.append(len(id_))
        days.append(day)
        ids.append(id_)
    datas = []
    for i in range(0, len(days)):
        day = days[i]
        id_ = ids[i]
        times_cost = calculate_time(day)
        way = find_shortest_path(calculate_all_pairs_shortest_paths(times_cost), len(day)-1)
        names = [list(day.keys())[way[i]] for i in range(0, len(way))]
        id_ = [id_[way[i]] for i in range(0, len(way))]
        cities = [day[name] for name in day.keys()]
        cities = [cities[way[i]] for i in range(0, len(way))]
        times, ways = calculate(cities)
        data = {
           "name": names,
           "times": times,
           "points": cities,
           "ways": ways,
           "id": id_
        }
        datas.append(data)

    return {"datas": datas}


@route.post("/picture", description="生成图片")
async def create_picture(pictures: List[UploadFile], info: str=Body(...)):
    file_paths = []
    for picture in pictures:
        contents = await picture.read()
        _, file_extension = os.path.splitext(picture.filename)
        # 获取当前时间的时间戳并格式化为字符串
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        # 创建文件名（使用时间戳和文件后缀）
        file_name = f"{timestamp}{file_extension}"
        file_path = "src/static/route/"+file_name
        file_paths.append(file_path)
        with open(file_path, "wb") as file:
            file.write(contents)
    save_file_path = await day_routes(file_paths, info)
    for file_path in file_paths:
        os.remove(file_path)
    return {"data": save_file_path}


@route.post("/save", description="保存路径")
async def save_route(user_id: str, info: str, name: str):
    user = await User.get_or_none(number=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    strategy =  await Strategy.create(strategy=info, user=user, name=name)
    return {"data": strategy.id}


@route.get("/{user_id}", description="得到用户的所有规划")
async def get_routes(user_id: str):
    user = await User.get_or_none(number=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    strategies = await user.strategy.all()  # 使用 related_name 查询该用户的所有策略
    data = []
    for strategy in strategies:
        user = await User.get_or_none(id=strategy.user_id)

        data.append({"strategy_id": strategy.id, "strategy_name": strategy.name, "user_name": user.username})

    # 返回数据
    return {"data": data}

@route.get("/route/{route_id}", description="得到一个规划")
async def get_routes(route_id: int):
    strategy = await Strategy.get_or_none(id=route_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="规划不存在")

    # 返回数据
    return {"data": json.loads(strategy.strategy)}

@route.delete("/{route_id}", description="删除一个规划")
async def delete_route(route_id: int):
    strategy = await Strategy.get_or_none(id=route_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="规划不存在")
    await strategy.delete()  # 删除记录

    return {"detail": "规划已删除"}