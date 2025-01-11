from src.model import *
from fastapi import HTTPException

async def double_user_exist(user1_number: str, user2_number: str):
    user1_exist = await User.get_or_none(number=user1_number)
    if user1_exist is None:
        raise HTTPException(status_code=404, detail="User with this phone number does not exist.")
    user2_exist = await User.get_or_none(number=user2_number)
    if user2_exist is None:
        raise HTTPException(status_code=404, detail="Friend with this phone number does not exist.")

async def ask_for_friend(user1_number: str, user2_number: str):
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
            raise HTTPException(status_code=400, detail="已是好友")
        elif friendship.status == 1:
            if small == user1_number:
                raise HTTPException(status_code=400, detail="好友请求已发送，请等待对方接受")
            else:
                friendship.status = 3
                await friendship.save()
                return "对方已发送好友申请，双向添加成功！"

        elif friendship.status == 2:
            if small == user1_number:
                friendship.status = 3
                await friendship.save()
                return "对方已发送好友申请，双向添加成功!"
            else:
                raise HTTPException(status_code=400, detail="好友请求已发送，请等待对方接受")
        else:
            if small == user1_number:
                friendship.status = 1
                await friendship.save()
                return "好友请求发送成功"
            else:
                friendship.status = 2
                await friendship.save()
                return "好友请求发送成功"

    else:
        if small == user1_number:
            await Friendship.create(user1_number=small, user2_numebr=large, status=1)
            return "好友请求发送成功"
        else:
            await Friendship.create(user1_number=small, user2_numebr=large, status=2)
            return "好友请求发送成功"

async def accept_as_friend(user1_number: str, user2_number: str):
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
            raise HTTPException(status_code=400, detail="已是好友")
        elif friendship.status == 1 and large == user1_number:
            friendship.status = 3
            await friendship.save()
            return "好友请求接受成功"
        elif friendship.status == 2 and small == user1_number:
            friendship.status = 3
            await friendship.save()
            return "好友请求接受成功"
        else:
            raise HTTPException(status_code=400, detail="未找到对方的好友申请记录")
    else:
        raise HTTPException(status_code=404, detail="未找到好友请求记录")

async def are_friend(user1_number: str, user2_number: str):
    if user1_number == user2_number:
        raise HTTPException(status_code=400, detail="无法判断自己为好友")
    elif user1_number > user2_number:
        small = user2_number
        large = user1_number
    else:
        small = user1_number
        large = user2_number

    friendship = await Friendship.filter(user1_number=small, user2_number=large, status=3).first()

    if friendship:
        return "true"
    return "false"