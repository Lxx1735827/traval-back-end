import aiofiles
import requests
import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from src.schema import *
from src.setting import *
from src.utils.passwordutils import *
from src.utils.codeutils import *
from src.utils.qrcode_utils import *

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
    save_path = save_directory+ f"/{number}{file_extension}"  # 例如: avatars/12345.jpg
    user_exist.avatar = save_path

    async with aiofiles.open(save_path, "wb") as buffer:
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
    user_exist.password = new_user.password
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

