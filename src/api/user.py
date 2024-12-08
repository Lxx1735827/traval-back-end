import os
import aiofiles

from fastapi import APIRouter, File, UploadFile, HTTPException
from src.schema import *
from src.setting import *

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import random
import json



user = APIRouter()


@user.get("/{user_number}", description="得到一个用户的所有信息")
async def get_user(user_number: str):
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")
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
        # 返回用户信息（排除敏感数据）
    user_data = {
        "number": user_exist.number,
        "username": user_exist.username,  # 假设你的 User 模型有一个 name 字段
        "avatar": user_exist.avatar,  # 假设有 email 字段
        "is_shown": user_exist.is_shown
    }
    return {"data": user_data}


@user.put('/avatar/{number}', description="修改头像")
async def update_avatar(number: str, avatar: UploadFile = File()):
    user_exist = await User.get_or_none(number=number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    save_directory = "static/user"  # 存放头像文件的目录
    file_extension = os.path.splitext(avatar.filename)[1]  # 获取文件的扩展名
    save_path = save_directory+ f"/{number}{file_extension}"  # 例如: avatars/12345.jpg
    user_exist.avatar = save_path

    async with aiofiles.open(save_path, "wb") as buffer:
        await buffer.write(await avatar.read())
    await user_exist.save()

    return {"data": save_path}


@user.put("/", description="修改用户信息")
async def update_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    # 如果用户不存在，返回 404 错误
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User not found.")
    # 更新用户信息
    user_exist.password = new_user.password
    user_exist.username = new_user.username

    # 保存更新
    await user_exist.save()
    return {"data": "用户信息更新成功"}


def generate_verification_code(length=6):
    return ''.join(random.choices('0123456789', k=length))
@user.get("/phone_verification/{phonenumer}", description="手机号获取短信验证码")
async def login_by_phone(phonenumer: str):

    user_exist = await User.get_or_none(number=phonenumer)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    user_data = {
        "number": user_exist.number,
        "username": user_exist.username,  # 假设你的 User 模型有一个 name 字段
        "avatar": user_exist.avatar,  # 假设有 email 字段
        "is_shown": user_exist.is_shown
    }

    PhoneNumber = phonenumer
    code = generate_verification_code(6)
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, template_code)

    # 创建CommonRequest实例
    request = CommonRequest()

    # 设置请求参数,下面这5行其实不用动
    request.set_accept_format('json')  # 设置API响应格式的方法
    request.set_domain('dysmsapi.aliyuncs.com')  # 设置API的域名的方法
    request.set_method('POST')  # 设置API请求方法
    request.set_version('2017-05-25')  # 设置API版本号
    request.set_action_name('SendSms')  # 设置API操作名

    # 设置短信模板参数
    request.add_query_param('PhoneNumbers', PhoneNumber)
    request.add_query_param('SignName', SIGN_NAME)
    request.add_query_param('TemplateCode', template_code)
    # request.add_query_param('TemplateParam', '{"code":"123456"}')
    template_param = {"code": code}
    request.add_query_param('TemplateParam', json.dumps(template_param))
    # 发送短信请求并获取返回结果
    response = acs_client.do_action_with_exception(request)

    print(response)

    return {"data": {"code": code, "user": user_data}}


