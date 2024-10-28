from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import ValidationError
from datetime import datetime

class User(Model):
    id = fields.IntField(pk=True, max_length=11)
    number = fields.CharField(max_length=11, description="电话号码")
    username = fields.CharField(max_length=20, description="用户名", default="username")
    password = fields.CharField(max_length=11, description="密码")
    avatar = fields.CharField(max_length=255, description="头像", default="static/site/默认头像.png")
    sites = fields.ManyToManyField("models.Site", related_name="User", through="user_site",
                                   description="用户收藏的景点")
    conversations = fields.ReverseRelation["Conversation"]
    # restaurants = fields.ManyToManyField("models.Restaurant", related_name="User", through="user_restuarant",
    #                                description="用户收藏的餐厅")

class Strategy(Model):
    id = fields.IntField(pk=True, max_length=11)
    strategy = fields.CharField(max_length=2048, description="攻略，日期加地点")
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
    # users = fields.ManyToManyField("models.User", related_name="Restaurant", through="user_restaurant",
    #                                description="喜欢该餐厅的用户")
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
    user_id = fields.IntField(description="用户ID")
    content = fields.TextField(description="评论内容", null=True)
    created_at = fields.DatetimeField(default=datetime.utcnow, description="记录时间")  # 添加记录时间属性




