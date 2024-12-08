from fastapi import APIRouter
from src.schema import *
from src.utils.routeutils import *

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
