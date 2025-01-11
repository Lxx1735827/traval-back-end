from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import ValidationError
from datetime import datetime


class User(Model):
    id = fields.IntField(pk=True, max_length=11)
    number = fields.CharField(max_length=11, description="电话号码")
    username = fields.CharField(max_length=20, description="用户名", default="username")
    password = fields.CharField(max_length=300, description="密码")
    salt = fields.CharField(max_length=300, description="盐", default="string")
    iter = fields.IntField(description="迭代次数", default=1000)
    avatar = fields.CharField(max_length=255, description="头像", default="static/user/默认头像.png")
    sites = fields.ManyToManyField("models.Site", related_name="User", through="user_site", description="用户收藏的景点")
    conversations = fields.ReverseRelation["Conversation"]
    restaurants = fields.ManyToManyField("models.Restaurant", related_name="User", through="user_restaurant", description="用户收藏的餐厅")
    visit_sites = fields.ManyToManyField("models.Site", related_name="visit_user", through="user_visit_site", description="用户访问过的的景点")
    check_sites = fields.ManyToManyField("models.Site", related_name="check_site_user", through="user_check_site", description="用户打卡的景点")
    check_restaurants = fields.ManyToManyField("models.Restaurant", related_name="check_restaurant_user", through="user_check_restaurant", description="用户打卡的餐厅")
    is_shown = fields.IntField(description="标识", default=1)
    strategy = fields.ReverseRelation["Strategy"]
    qrcode = fields.CharField(max_length=255, description="二维码", default="static/qrcode/0.png")

class Friendship(Model):
    id = fields.IntField(pk=True)
    user1_numebr = fields.CharField(max_length=11, description="user1电话号码") #小
    user2_numebr = fields.CharField(max_length=11, description="user2电话号码") #大
    status = fields.IntField(description="是否加为好友", default=0) # 0:均未申请 1:小向大发出申请 2:大向小发出申请 3:结为好友
    content = fields.CharField(max_length=10000, description="历史对话")



class Text(Model):
    id = fields.IntField(pk=True, max_length=11)
    phonenumber = fields.CharField(max_length=11, description="电话号码")
    code = fields.CharField(max_length=6, description="短信验证码 ")


class Strategy(Model):
    id = fields.IntField(pk=True, max_length=11)
    strategy = fields.TextField(description="攻略，日期加地点")
    name = fields.CharField(max_length=11, description="名字", default="旅游攻略")
    user = fields.ForeignKeyField("models.User", related_name="strategy", on_delete=fields.SET_NULL, null=True)


class Site(Model):
    id = fields.IntField(pk=True, max_length=11)
    name = fields.CharField(max_length=100, description="景点名字")
    city = fields.CharField(max_length=20, description="城市")
    description = fields.CharField(max_length=2000, description="景点简介", null=True)
    picture = fields.CharField(max_length=255, description="景点图片", default="static/site/默认图片.png")
    location = fields.CharField(max_length=255, description="景点地址")
    telephone = fields.CharField(max_length=255, description="景点联系电话", null=True)
    time_reference = fields.CharField(max_length=255, description="景点用时参考", null=True)
    transport = fields.TextField(description="交通参考", null=True)
    ticket = fields.CharField(max_length=3000, description="景点门票", null=True)
    open_time = fields.CharField(max_length=2000, description="景点开放时间", null=True)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, description="经度", default=None)
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, description="纬度", default=None)
    users = fields.ManyToManyField("models.User", related_name="Site", through="user_site",
                                   description="喜欢该景点的用户")
    visit_users = fields.ManyToManyField("models.User", related_name="visit_site", through="user_visit_site",
                                   description="访问过该景点的用户")
    check_users = fields.ManyToManyField("models.User", related_name="check_site", through="user_check_site",
                                   description="打卡过该景点的用户")
    # review_1 = fields.TextField(description="景点评论", null=True)
    # review_2 = fields.TextField(description="景点评论", null=True)
    # review_3 = fields.TextField(description="景点评论", null=True)
    # review_4 = fields.TextField(description="景点评论", null=True)
    # review_5 = fields.TextField(description="景点评论", null=True)

    type = fields.CharField(max_length=50, description="对象类型", default="景点")  # 添加type属性


class Restaurant(Model):
    id = fields.IntField(pk=True, max_length=11)
    name = fields.CharField(max_length=100, description="餐厅名字")
    city = fields.CharField(max_length=20, description="城市")
    image = fields.CharField(max_length=255, description="餐厅图片", default="static/restaurant/默认图片.png")
    location = fields.CharField(max_length=500, description="餐厅地址")
    telephone = fields.CharField(max_length=100, description="餐厅联系电话", null=True)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, description="经度", default=None)
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, description="纬度", default=None)
    users = fields.ManyToManyField("models.User", related_name="Restaurant", through="user_restaurant",
                                   description="喜欢该餐厅的用户")
    check_users = fields.ManyToManyField("models.User", related_name="check_restaurant", through="user_check_restaurant",
                                   description="打卡过该餐厅的用户")
    # review_1 = fields.TextField(description="餐厅评论", null=True)
    # review_2 = fields.TextField(description="餐厅评论", null=True)
    # review_3 = fields.TextField(description="餐厅评论", null=True)
    # review_4 = fields.TextField(description="餐厅评论", null=True)
    # review_5 = fields.TextField(description="餐厅评论", null=True)

    type = fields.CharField(max_length=50, description="对象类型", default="餐厅")  # 添加type属性


class Conversation(Model):
    id = fields.IntField(pk=True, max_length=11)
    content = fields.CharField(max_length=10000, description="历史对话")
    user = fields.ForeignKeyField("models.User", related_name="Conversation", on_delete=fields.SET_NULL, null=True)


class Review(Model):
    id = fields.IntField(pk=True, max_length=12)
    entity_id = fields.IntField(description="景点或餐厅ID")  # 合并为同一列
    entity_type = fields.CharField(max_length=50, description="类型", choices=["景点", "餐厅"])  # 区分类型
    user_number = fields.CharField(max_length=11, description="电话号码")
    content = fields.TextField(description="评论内容", null=True)
    created_at = fields.DatetimeField(default=datetime.utcnow, description="记录时间")  # 添加记录时间属性


class Video(Model):
    id = fields.IntField(pk=True, max_length=12)
    entity_id = fields.IntField(description="景点或餐厅ID")  # 合并为同一列
    video = fields.CharField(max_length=100, description="视频地址", default="static/video/默认视频.mp4")


class SiteRelationship(Model):
    relate_id = fields.IntField(pk=True, max_length=11)
    site_from_ids = fields.CharField(max_length=2000)
    site_to_ids = fields.CharField(max_length=2000)

