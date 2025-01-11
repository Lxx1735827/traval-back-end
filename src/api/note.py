import os
import re
import aiofiles
import time
from fastapi import APIRouter, HTTPException
from fastapi import UploadFile
from typing import List

from src.model import Note, User, NoteReview

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
        async with aiofiles.open(file_path, "wb") as buffer:
            await buffer.write(await file.read())
        pictures += file_path+"###"
    await Note.create(name=name, picture=pictures, content=content, user=exist_user, tag=tag)

    return {"data": "生成成功"}


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
    reviews = await NoteReview.filter(id=note_id).all()
    data = []
    for review in reviews:
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
    if note_ is Note:
        raise HTTPException(status_code=404, detail="笔记不存在")

    data = {
        "user_number": note_.user.number,
        "user_avatar": note_.user.avatar,
        "user_name": note_.user.username,
        "pictures": note_.picture,
        "name": note_.name,
        "content": note_.content
    }
    return {"data": data}


@note.post("/review", description="笔记评论")
async def note_review(number: str, note_id: int, content: str, create_time: str):
    review = await NoteReview.create(entity_id=note_id, user_number=number, content=content, created_at=create_time)

    return {"评论id": review.id}



