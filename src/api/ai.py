from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException
from src.schema import *

ai = APIRouter()


@ai.post("/", description="生成对话")
async def create_conversation():
    # now = datetime.now()
    # formatted_time = now.strftime('%Y-%m-%d %H-%M')
    # content = formatted_time + ":" + content + ";"
    #
    # exist_user = User.get_or_none(number=number)
    # if exist_user is None:
    #     raise HTTPException(status_code=404, detail="该用户不存在")
    # print(content)
    # await Conversation.create(content=content, user=exist_user)
    return {"data": "创建成功"}

@ai.get("/")
async def get_all():
    return {"data": "data"}
