import os
import shutil

import pandas as pd
from tortoise import Tortoise, run_async
from src.model import Site
import requests
import json
import time

baseurl = "https://restapi.amap.com/v3/geocode/geo?address="

async def run():
    # 初始化 Tortoise ORM
    await Tortoise.init(
        db_url="mysql://root:082231@localhost:3306/travel",
        modules={'models': ["src.model", "aerich.models"]}
    )
    await Tortoise.generate_schemas()

    # 指定根目录（父文件夹）
    root_directory = r'D:\All_Type_Save\Python\scheduleapp\details'

    # 遍历根目录下的所有子文件夹
    for city_folder in os.listdir(root_directory):
        city_folder_path = os.path.join(root_directory, city_folder)

        # 检查是否为子文件夹
        if os.path.isdir(city_folder_path):
            # 遍历子文件夹中的 CSV 文件
            for filename in os.listdir(city_folder_path):
                if filename.endswith('.csv'):
                    base_name = os.path.splitext(filename)[0]
                    # 使用 "_" 分隔字符串
                    parts = base_name.split("_")
                    # 假设文件名格式为 city_name.csv，分离出 city 和 name
                    if len(parts) >= 2:
                        city = parts[0]
                        name = "_".join(parts[1:])  # 可能存在下划线的名称部分
                    else:
                        city, name = "虚拟城市", "虚拟景点"

                    existing_site = await Site.get_or_none(name=name, city=city)
                    if existing_site:
                        print(f"Site '{name}' in city '{city}' already exists. Skipping insertion.")
                        continue  # 如果存在，跳过插入

                    file_path = os.path.join(city_folder_path, filename)
                    # 读取 CSV 文件
                    df = pd.read_csv(file_path)
                    # 将数据逐行插入数据库
                    for index, row in df.iterrows():
                        # 默认值设置
                        location = str(row["location"]).strip() if pd.notna(row["location"]) and str(
                            row["location"]).strip() != "" else "暂无详细地址"
                        summary = str(row["summary"]).strip() if pd.notna(row["summary"]) and str(
                            row["summary"]).strip() != "" else "暂无介绍"
                        telephone = str(row["telephone"]).strip() if pd.notna(row["telephone"]) and str(
                            row["telephone"]).strip() != "" else "暂无联系电话"
                        time_reference = str(row["time_reference"]).strip() if pd.notna(row["time_reference"]) and str(
                            row["time_reference"]).strip() != "" else "暂无参考游玩时间"
                        transport = str(row["transport"]).strip() if pd.notna(row["transport"]) and str(
                            row["transport"]).strip() != "" else "暂无推荐交通方式"
                        ticket = str(row["ticket"]).strip() if pd.notna(row["ticket"]) and str(
                            row["ticket"]).strip() != "" else "无门票"
                        open_time = str(row["open_time"]).strip() if pd.notna(row["open_time"]) and str(
                            row["open_time"]).strip() != "" else "全天开放"

                        # 处理经纬度 API 请求
                        url = baseurl + location + name + "&output=JSON&key=9643b9d52170cf6bdb7f7cab574400a2"
                        response = requests.get(url=url).text
                        content = json.loads(response)
                        if content["status"] == "1":
                            longitude, latitude = content["geocodes"][0]["location"].split(",")
                        else:
                            # 若未找到，使用 city 进行查找
                            url = baseurl + city + "&output=JSON&key=9643b9d52170cf6bdb7f7cab574400a2"
                            response = requests.get(url=url).text
                            content = json.loads(response)
                            longitude, latitude = content["geocodes"][0]["location"].split(",")

                        reviews = ["不错，推荐"] * 5
                        for i in range(1, 6):
                            review_column = f"review_{i}"
                            if review_column in row:  # 检查是否存在该列
                                reviews[i - 1] = row[review_column] if row[review_column] else "不错，推荐"

                        # 插入数据到 Site 表
                        await Site.create(
                            name=name,
                            city=city,
                            description=summary,
                            picture=f"static/site/{city}/{name}/{city}_{name}1",
                            location=location,
                            telephone=telephone,
                            time_reference=time_reference,
                            transport=transport,
                            ticket=ticket,
                            open_time=open_time,
                            longitude=longitude,
                            latitude=latitude,
                            review_1=reviews[0],
                            review_2=reviews[1],
                            review_3=reviews[2],
                            review_4=reviews[3],
                            review_5=reviews[4],
                        )
                        print(f"{city}_{name} has been stored to database")
                        time.sleep(0.5)

            shutil.rmtree(city_folder_path)


    # 关闭数据库连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(run())