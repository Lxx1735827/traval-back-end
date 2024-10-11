from fastapi import APIRouter
from fastapi import HTTPException
from src.schema import *

user = APIRouter()




@user.get("/{user_number}", description="得到一个用户的所有信息")
async def get_user(user_number:str):
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is not None:
        raise HTTPException(status_code=400, detail="User with this phone number already exists.")
    return {"data": user_exist}


@user.post("/", description="添加新用户")
async def add_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    if user_exist is not None:
        raise HTTPException(status_code=400, detail="User with this phone number already exists.")
    # 验证码 TODO

    # 插入数据库
    await User.create(**new_user.dict())
    return {"data": "插入成功"}


@user.post('/login', description="登录")
async def login_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User not found.")
    if new_user.password != user_exist.password:
        raise HTTPException(status_code=400, detail="The password is incorrect")
    # 验证码 TODO

    return {"data": "登陆成功"}



@user.put("/", description="修改用户信息")
async def update_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    # 如果用户不存在，返回 404 错误
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User not found.")
    # 更新用户信息
    user_exist.password = new_user.password
    user_exist.avatar = new_user.avatar
    # 保存更新
    await user_exist.save()
    return {"data": "用户信息更新成功"}







