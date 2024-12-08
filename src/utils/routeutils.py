import requests
import heapq
import sys
import math
from src.setting import *
from fastapi import HTTPException


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    计算两个经纬度之间的距离 (单位：公里)

    参数:
    lat1, lon1: 第一个点的纬度和经度
    lat2, lon2: 第二个点的纬度和经度

    返回:
    返回两点之间的距离，单位为公里
    """

    # 将经纬度从度转换为弧度
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 哈弗辛公式
    dlat = lat2 - lat1  # 纬度差
    dlon = lon2 - lon1  # 经度差

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # 地球半径 (公里)
    radius = 6371

    # 计算两点之间的距离
    distance = radius * c
    return distance


def get_walk_time(city1: dict, city2: dict):
    city1_location = str(city1["longitude"]) + "," + str(city1["latitude"])
    city2_location = str(city2["longitude"]) + "," + str(city2["latitude"])
    url = WALKURL
    param = {
        "key": GAODEKEY,
        "origin": city1_location,
        "destination": city2_location,
        "strategy": 0
    }
    respond = requests.get(url=url, params=param)
    if respond.json()["status"] == "1":
        return int(respond.json()["route"]["paths"][0]["cost"]["duration"])/3600
    else:
        raise HTTPException(status_code=400, detail="获取时间失败")


def get_car_time(city1: dict, city2: dict):
    city1_location = str(city1["longitude"]) + "," + str(city1["latitude"])
    city2_location = str(city2["longitude"]) + "," + str(city2["latitude"])
    url = CARURL
    param = {
        "key": GAODEKEY,
        "origin": city1_location,
        "destination": city2_location,
        "strategy": 0
    }
    respond = requests.get(url=url, params=param)
    if respond.json()["status"] == "1":
        return int(respond.json()["route"]["paths"][0]["duration"])/3600
    else:
        raise HTTPException(status_code=400, detail="获取时间失败")


def calculate_time(city_list: dict):
    """

    :param city_list: {city1: {latitude, longitude}}
    :return:
    """
    n = len(city_list.keys())  # 例如创建一个5x5的数组
    city_times = [[0 for _ in range(n)] for _ in range(n)]
    cities = list(city_list.keys())
    for i in range(0, n):
        for j in range(i, n):
            if i == j:
                city_times[i][j] = 10000
            else:
                city1 = cities[i]
                city2 = cities[j]
                time_walk = calculate_distance(city_list[city1]["latitude"], city_list[city1]["longitude"],
                                               city_list[city2]["latitude"], city_list[city2]["longitude"])
                city_times[i][j] = time_walk
                city_times[j][i] = time_walk
    return city_times


def dijkstra(time_cost, start):
    n = len(time_cost)
    # 初始化最短时间，start 点到自己为 0，其它为无限大
    dist = [float('inf')] * n
    dist[start] = 0
    # 使用最小堆来存储当前已访问的节点
    heap = [(0, start)]  # (当前距离, 当前节点)

    while heap:
        current_dist, node = heapq.heappop(heap)

        # 如果当前的距离已经大于当前已知的最短距离，跳过
        if current_dist > dist[node]:
            continue

        # 更新相邻节点的最短路径
        for neighbor in range(n):
            if time_cost[node][neighbor] != float('inf'):  # 如果有路径
                new_dist = current_dist + time_cost[node][neighbor]
                if new_dist < dist[neighbor]:  # 如果新路径更短，更新
                    dist[neighbor] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor))

    return dist  # 如果没有路径返回终点的最短路径


def calculate_all_pairs_shortest_paths(time_cost: list):
    n = len(time_cost)
    shortest_path = [[float('inf')] * n for _ in range(n)]

    for i in range(n):
        shortest_path[i] = dijkstra(time_cost, i)

    return shortest_path


def dfs(curr_point, visited, dist, n, current_distance, min_distance, num_visited, current_path, best_path, end_point):
    # 如果已经访问过所有点，且当前点为终点，更新最短路径
    if num_visited == n and curr_point == end_point:
        if current_distance < min_distance[0]:
            min_distance[0] = current_distance
            best_path[:] = current_path[:]  # 更新最短路径
        return

    # 剪枝：如果当前路径的距离已经超过了当前的最短距离，直接返回
    if current_distance >= min_distance[0]:
        return

    # 遍历所有点，选择下一个未访问的点进行递归
    for next_point in range(n):
        if not visited[next_point]:  # 如果未访问过该点
            visited[next_point] = True  # 标记为已访问
            current_path.append(next_point)  # 记录当前路径
            dfs(next_point, visited, dist, n, current_distance + dist[curr_point][next_point], min_distance, num_visited + 1, current_path, best_path, end_point)
            current_path.pop()  # 回溯时移除最后一个点
            visited[next_point] = False  # 回溯时标记为未访问


def find_shortest_path(dist, end_point):
    n = len(dist)  # 获取图的节点数
    visited = [False] * n  # 记录每个节点是否被访问
    visited[0] = True  # 起点已访问
    min_distance = [sys.maxsize]  # 记录最短路径，初始化为无穷大
    best_path = []  # 记录最短路径的节点序列
    current_path = [0]  # 当前路径，从起点出发
    dfs(0, visited, dist, n, 0, min_distance, 1, current_path, best_path, end_point)  # 从起点（0）出发，已访问1个节点
    return best_path


def calculate(city_list: list):
    times = []
    ways = []
    for i in range(1, len(city_list)):
        if calculate_distance(city_list[i]["latitude"], city_list[i]["longitude"], city_list[i-1]["latitude"], city_list[i-1]["longitude"]) < 1:
            respond = get_walk_time(city_list[i-1], city_list[i])
            ways.append(0)
            times.append(respond)
        else:
            respond = get_car_time(city_list[i - 1], city_list[i])
            ways.append(1)
            times.append(respond)
    return times, ways


# if __name__ == "__main__":
#     citys = {
#         "1906创意工厂": {"latitude": 30.613708, "longitude": 104.083161},
#         "兰桂坊成都": {"latitude": 30.643029, "longitude": 104.084482},
#         "三和老爷车博物馆": {"latitude": 30.597103, "longitude": 104.04128},
#         "三国茶园": {"latitude": 30.640942, "longitude": 104.042081},
#         "九眼桥": {"latitude": 30.639417, "longitude": 104.088167},
#     }
#     times_cost = calculate_time(citys)
#
#     second = find_shortest_path(calculate_all_pairs_shortest_paths(times_cost), 4)
#     citys = [citys[name] for name in citys.keys()]
#     print(calculate(citys))
