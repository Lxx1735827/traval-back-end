from PIL import Image
import qrcode
import os
from src.model import *
from fastapi import HTTPException

async def get_qrcode(source: str, user_number: str) -> None:
    """
    生成二维码
    :param source: 保存路径
    :param data: 数据
    :return:
    """
    user_exist = await User.get_or_none(number=user_number)
    if user_exist is None:
        print("QRcode exception: User with this phone number does not exist.")
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")

    user_exist.qrcode = f"static/qrcode/{user_number}.png"

    if not os.path.exists(source):
        os.makedirs(source)

    qr = qrcode.QRCode(
        version=2,  # 尺寸
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 容错信息当前为 30% 容错
        box_size=10,  # 每个格子的像素大小
        border=4  # 边框格子宽度
    )  # 设置二维码的大小
    try:
        qr.add_data(user_exist.number)
        print("qr.add_data")

        # 生成二维码图片，fill_color二维码颜色，back_color二维码背景颜色
        img = qr.make_image(fill_color='purple', back_color="white")
        # 用user_number命名文件
        filename = user_exist.number + '.jpg'
        file = source + "/" + filename
        # 添加logo，打开logo照片
        icon = Image.open(user_exist.avatar)
        print("icon")
        # 获取图片的宽高
        img_w, img_h = img.size
        # 参数设置logo的大小
        factor = 4
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        # 重新设置logo的尺寸
        icon = icon.resize((icon_w, icon_h))
        # 得到画图的x，y坐标，居中显示
        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        # 黏贴logo照
        img.paste(icon, (w, h), mask=None)
        # 保存
        img.save(file)
        print(f"QR Code {filename} produced!")
        return file
    except Exception as e:
        print(f"Failed to produce QR Code：{e}")



