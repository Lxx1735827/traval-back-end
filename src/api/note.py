import os
import re
import aiofiles
import time
from datetime import date
from fastapi import APIRouter, HTTPException
from tortoise.expressions import Q
from fastapi import UploadFile
from typing import List

from src.model import Note, User, NoteReview, Recommend
from src.utils.hotutils import *
from src.utils.aiutils3 import create_picture

note = APIRouter()


@note.post("/", description="生成笔记")
async def create_note(number: str,  name: str, content: str, files: List[UploadFile], tag: int = -1):
    exist_user = await User.filter(number=number).first()
    if exist_user is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    pictures = ""
    for file in files:
        timestamp_ms = str(time.time() * 1000)
        file_suffix = file.filename.split(".")[-1]
        file_path = "static/note/" + timestamp_ms + "." + file_suffix
        async with aiofiles.open("src/" + file_path, "wb") as buffer:
            await buffer.write(await file.read())
        pictures += file_path+"###"
    await Note.create(name=name, picture=pictures, content=content, user=exist_user, tag=tag)

    return {"data": "生成成功"}


@note.get("/create-hot", description="定时更新热点")
async def create_hot():
    # 更新旅游热点
    hots = get_hot()
    for hot in hots:
        create_picture(hot, "src/static/hot/"+hot+".jpg")
        current_date = str(date.today())
        sites = get_sites_(hot)
        ids = ""
        for site in sites:
            try:
                city, name, description = get_info(site)
                location, longitude, latitude = get_location(site, city)
                create_picture(name, "src/static/site/"+name+".jpg")
                site_data = {
                    "name": name,
                    "city": city,
                    "description": description,
                    "location": location,
                    "longitude": longitude,
                    "latitude": latitude,
                    "picture": "static/site/"+name+".jpg"
                }
                site_ = await Site.create(**site_data)
                ids += str(site_.id) + ","
            except:
                continue
        await Recommend.create(tag="热点", name=hot, sites_id=ids, day_time=current_date, picture="static/hot/"+hot+".jpg")
    return {"data": "success"}


@note.get("/create-people", description="文人路线")
async def create_people(people: str, sites: str):
    sites = sites.split(",")
    create_picture(people, "src/static/hot/" + people + ".jpg")
    current_date = str(date.today())
    ids = ""
    for site in sites:
        try:
            city, name, description = get_info(site)
            location, longitude, latitude = get_location(site, city)
            create_picture(name, "src/static/site/" + name + ".jpg")
            site_data = {
                "name": name,
                "city": city,
                "description": description,
                "location": location,
                "longitude": longitude,
                "latitude": latitude,
                "picture": "static/site/" + name + ".jpg"
            }
            site_ = await Site.create(**site_data)
            ids += str(site_.id) + ","
        except:
            continue
    await Recommend.create(tag="文人", name=people, sites_id=ids, day_time=current_date,
                           picture="static/hot/" + people + ".jpg")
    return {"data": "success"}


@note.get("/create-book", description="书籍路线")
async def create_book(book: str, sites: str):
    sites = sites.split(",")
    # create_picture(book, "static/hot/" + book + ".jpg")
    current_date = str(date.today())
    ids = ""
    for site in sites:
        try:
            city, name, description = get_info(site)
            location, longitude, latitude = get_location(site, city)
            create_picture(name, "src/static/site/" + name + ".jpg")
            site_data = {
                "name": name,
                "city": city,
                "description": description,
                "location": location,
                "longitude": longitude,
                "latitude": latitude,
                "picture": "static/site/" + name + ".jpg"
            }
            site_ = await Site.create(**site_data)
            ids += str(site_.id) + ","
        except:
            continue
    await Recommend.create(tag="书籍", name=book, sites_id=ids, day_time=current_date,
                           picture="static/hot/" + book + ".jpg")
    return {"data": "success"}


@note.get("/get-recommend/{tag}", description="获得推荐目录")
async def get_recommend(tag: str):
    datas = await Recommend.filter(tag=tag)
    info = [{"id": data.id, "name": data.name, "picture": data.picture} for data in datas]
    return {"data": info}


@note.get("/get-sites/{tag_id}", description="获得景点")
async def get_sites(tag_id: int):
    datas = await Recommend.get_or_none(id=tag_id)
    sites_id = datas.sites_id[:-1].split(',')
    sites_id = [int(site) for site in sites_id]
    sites = await Site.filter(id__in=sites_id).all()
    info = [{"id": site.id, "name": site.name, "picture": site.picture, "description": site.description, "location": site.location, "latitude": site.latitude, "longitude": site.longitude} for site in sites]
    return {"data": info}


@note.get("/{user_id}", description="获得用户所有笔记")
async def notes_get(user_id: str):
    user = await User.get_or_none(number=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    notes = await Note.filter(user=user).all()
    data = []
    for note_ in notes:
        picture = note_.picture.split("##")[0]
        data.append({
            "id": note_.id,
            "name": note_.name,
            "picture": picture
        })

    return {"data": data}


@note.get("/note/reviews", description="获取一个笔记的所有评论")
async def note_reviews(note_id: int):
    reviews = await NoteReview.filter(entity_id=note_id).all()
    data = []
    for review in reviews:
        print(type(review.user_number))
        print(review.user_number)
        user = await User.filter(number=review.user_number).first()
        data.append({
            "id": review.id,
            "user_number": review.user_number,
            "user_avatar": user.avatar,
            "content": review.content,
            "create_time": review.created_at
        })

    return {"data": data}

@note.get("/note/{note_id}", description="获得一个笔记的所有信息")
async def note_get(note_id: int):
    note_ = await Note.filter(id=note_id).select_related('user').first()
    if note_ is None:
        raise HTTPException(status_code=404, detail="笔记不存在")
    data = {
        "user_number": note_.user.number,
        "user_avatar": note_.user.avatar,
        "user_name": note_.user.username,
        "pictures": note_.picture,
        "name": note_.name,
        "content": note_.content,
        "tag": note_.tag
    }
    return {"data": data}


@note.post("/review", description="笔记评论")
async def note_review(number: str, note_id: int, content: str, create_time: str):
    review = await NoteReview.create(entity_id=note_id, user_number=number, content=content, created_at=create_time)

    return {"评论id": review.id}


@note.post("/recommend", description="笔记推送")
async def note_recommend(number: str):
    notes = await Note.filter().all()
    notes = notes[-10:]
    data = []
    for note_ in notes:
        picture = note_.picture.split("##")[0]
        data.append({
            "id": note_.id,
            "name": note_.name,
            "picture": picture
        })

    return {"data": data}