import re

import aiofiles
import requests
import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from src.schema import *
from src.setting import *
from src.utils.passwordutils import *
from src.utils.codeutils import *
from src.utils.qrcode_utils import *
from src.utils.friend_utils import *

bc_url = "http://localhost:8000/bc"  # 区块链API的基础URL
user = APIRouter()

# 封装区块链交易请求的函数
async def add_transaction_to_blockchain(tx_data: dict):
    """向区块链提交交易数据"""
    try:
        response = requests.post(f"{bc_url}/new_transaction", json=tx_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to add transaction to blockchain")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error connecting to blockchain API")


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
    data = new_user.dict()
    salt, derived_key, iterations = generate_password_hash(data["password"])
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    derived_key_hex = binascii.hexlify(derived_key).decode('utf-8')
    data["password"] = derived_key_hex
    data["salt"] = salt_hex
    await User.create(**data)
    source_path = r'static/qrcode'
    file = await get_qrcode(source_path, new_user.number)

    tx_data = {
        "content": f"New user {new_user.number} is added to the database.",
        "timestamp": time.time()
    }
    # await add_transaction_to_blockchain(tx_data)

    return {"data": "插入成功"}


@user.post('/login', description="登录")
async def login_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User not found.")
    stored_salt = bytes.fromhex(user_exist.salt)
    stored_derived_key = bytes.fromhex(user_exist.password)
    is_valid = verify_password(new_user.password, stored_salt, stored_derived_key, user_exist.iter)
    if not is_valid:
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
async def update_avatar(number: str, avatar: UploadFile = File(...)):
    user_exist = await User.get_or_none(number=number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="该用户不存在")

    save_directory = "static/user"  # 存放头像文件的目录
    file_extension = os.path.splitext(avatar.filename)[1]  # 获取文件的扩展名
    timestamp_ms = int(time.time() * 1000)
    save_path = save_directory+ f"/{timestamp_ms}{file_extension}"  # 例如: avatars/12345.jpg
    user_exist.avatar = save_path

    async with aiofiles.open("src/"+save_path, "wb") as buffer:
        await buffer.write(await avatar.read())
    await user_exist.save()

    tx_data = {
        "content": f"User {number} changes its avatar.",
        "timestamp": time.time()
    }
    # await add_transaction_to_blockchain(tx_data)

    return {"data": save_path}


@user.put("/", description="修改用户信息")
async def update_user(new_user: UserSchema):
    # 查看是否已经存在
    user_exist = await User.get_or_none(number=new_user.number)
    # 如果用户不存在，返回 404 错误
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User not found.")
    # 更新用户信息
    salt, derived_key, iterations = generate_password_hash(new_user.password)
    salt_hex = binascii.hexlify(salt).decode('utf-8')
    derived_key_hex = binascii.hexlify(derived_key).decode('utf-8')
    user_exist.password = derived_key_hex
    user_exist.salt = salt_hex
    user_exist.username = new_user.username

    # 保存更新
    await user_exist.save()

    tx_data = {
        "content": f"User {new_user.number} changes its information.",
        "timestamp": time.time()
    }
    # await add_transaction_to_blockchain(tx_data)

    return {"data": "用户信息更新成功"}


@user.get("/code_send/{phonenumber}", description="手机号获取短信验证码")
async def send_code(phonenumber: str):
    print("send_code")
    code = await code_sender(phonenumber)

    phone_exist = await Text.get_or_none(phonenumber=phonenumber)
    if phone_exist is None:
        await Text.create(phonenumber=phonenumber, code=code)
    else:
        phone_exist.code = code
        await phone_exist.save()

    return {"data": {"code": code}}


@user.post("/code_verify", description="验证手机号的验证码")
async def verify_code(phonenumber: str, code: str):
    # 查询数据库中的记录
    phone_exist = await Text.get_or_none(phonenumber=phonenumber)

    if phone_exist is None:
        # 如果手机号不存在
        raise HTTPException(status_code=404, detail="Have never sent code text to this phone.")

    # 验证验证码是否正确
    if phone_exist.code == code:
        return {"data": "true"}
    else:
        return {"data": "false"}

@user.delete("/delete_user", description="删除用户")
async def delete_user(phonenumber: str):
    # 查询数据库中的记录
    phone_exist = await User.get_or_none(number=phonenumber)

    if phone_exist is None:
        # 如果手机号不存在
        raise HTTPException(status_code=404, detail="用户不存在")
    await phone_exist.delete()

    tx_data = {
        "content": f"User {phonenumber} is deleted.",
        "timestamp": time.time()
    }
    # await add_transaction_to_blockchain(tx_data)

    return {"data": "删除成功"}

@user.get("/qrcode/{user_number}", description="生成并获取用户的二维码")
async def qrcode(user_number: str):
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")
    # file = user_exist.qrcode
    if user_exist.qrcode == 'static/qrcode/0.png':
        source_path = r'static/qrcode'
        file = await get_qrcode(source_path, user_number)
    else:
        file = user_exist.qrcode
    return {"data": file}

@user.post("/friend/ask", description="user1向user2发送添加好友请求")
async def friend_ask(user1_number: str, user2_number: str):
    await double_user_exist(user1_number, user2_number)

    msg = await ask_for_friend(user1_number, user2_number)

    return {"data": msg}

@user.post("/friend/accept", description="user2接受user1的好友添加请求")
async def friend_accept(user1_number: str, user2_number: str):
    await double_user_exist(user1_number, user2_number)

    msg = await accept_as_friend(user1_number, user2_number)

    return {"data": msg}

@user.post("/friend/if", description="判断2个user是否为好友")
async def friend_if(user1_number: str, user2_number: str):
    await double_user_exist(user1_number, user2_number)

    msg = await are_friend(user1_number, user2_number)

    return {"data": msg}

@user.delete("/friend/delete", description="删除好友")
async def delete_friend(user1_number: str, user2_number: str):
    await double_user_exist(user1_number, user2_number)

    if user1_number == user2_number:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")
    elif user1_number > user2_number:
        small = user2_number
        large = user1_number
    else:
        small = user1_number
        large = user2_number

    friendship = await Friendship.filter(user1_number=small, user2_number=large).first()

    if friendship:
        if friendship.status == 3:
            friendship.status = 0
            await friendship.save()
            return {"data": "好友删除成功"}
        else:
            raise HTTPException(status_code=400, detail="目前二人还不是好友")
    else:
        raise HTTPException(status_code=404, detail="未找到好友记录")

@user.get("/friend/{user_number}", description="获取用户的好友列表")
async def user_all_friend(user_number: str):
    print("get into")
    # 检查用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")

    friendships = await Friendship.filter(
        (Q(user1_number=user_number) | Q(user2_number=user_number))& Q(status=3)
    )
    print("friendships")
    if not friendships:
        return {"user_number": user_number, "friends_list": []}

    # 提取好友号码
    friend_numbers = [
        friendship.user2_number if friendship.user1_number == user_number else friendship.user1_number
        for friendship in friendships
    ]
    print("friend_numbers")
    # 获取好友详细信息
    friends = await User.filter(number__in=friend_numbers).values("id", "number", "username", "avatar", "qrcode")
    return {
        "user_number": user_number,
        "friends_list": friends
    }


@user.post("/search", description="关键词搜索用户")
async def search_user(key: str):
    key_parts = list(key)
    numbers_set = set()  # 使用集合来去重
    print(key_parts)
    for key_part in key_parts:
        # 查找匹配用户名的用户
        numbers = await User.filter(Q(username__icontains=key_part)).values("number")
        for number in numbers:
            numbers_set.add(number['number'])
    users_list = await User.filter(number__in=list(numbers_set)).values("id", "number", "username", "avatar", "qrcode")
    return {"key": key, "results": users_list}



@user.post("/friend/search", description="关键词搜索用户的好友")
async def search_friend(user_number: str, key: str):
    # 检查用户是否存在
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")

    # 获取用户的好友关系
    friendships = await Friendship.filter(
        (Q(user1_number=user_number) | Q(user2_number=user_number)) & Q(status=3)
    )
    if not friendships:
        return {"user_number": user_number, "key": key, "results": []}

    # 提取好友的电话号码
    friend_numbers = [
        friendship.user2_number if friendship.user1_number == user_number else friendship.user1_number
        for friendship in friendships
    ]

    key_parts = list(key)
    numbers_set = set()  # 使用集合来去重
    print(key_parts)
    for key_part in key_parts:
        # 查找匹配用户名的用户
        numbers = await User.filter(number__in=friend_numbers).filter(Q(username__icontains=key_part)).values("number")
        for number in numbers:
            numbers_set.add(number['number'])

    users_list = await User.filter(number__in=list(numbers_set)).values("id", "number", "username", "avatar", "qrcode")

    return {
        "user_number": user_number,
        "key": key,
        "results": users_list
    }

@user.get("/friend/ask/{user_number}", description="获取用户的被申请好友列表")
async def get_friend_ask(user_number: str):
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")

    friendships = await Friendship.filter(
        (Q(user1_number=user_number) & Q(status=2)) | (Q(user2_number=user_number) & Q(status=1))
    )
    users_list = []
    if friendships:
        friend_numbers = [
            friendship.user2_number if friendship.user1_number == user_number else friendship.user1_number
            for friendship in friendships
        ]
        users_list = await User.filter(number__in=list(friend_numbers)).values("id", "number", "username", "avatar", "qrcode")
    return {"user_number": user_number, "asked_friend": users_list}
# @user.post("/wechat", description="转发消息到微信")
# async def send_wechat(user_number: str, msg: str):


@user.get("/footprint/{user_number}", description="生成历史足迹")
async def get_footprint(user_number: str):
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")
    sites = user_exist.visit_sites
    for site in sites:
        print(site.id)












