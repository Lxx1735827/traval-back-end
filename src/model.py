from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True, max_length=11)
    number = fields.CharField(max_length=11, description="电话号码")
    username = fields.CharField(max_length=20, description="用户名", default="username")
    password = fields.CharField(max_length=11, description="密码")
    avatar = fields.CharField(max_length=255, description="头像", default="static/user/默认头像.png")
    sites = fields.ManyToManyField("models.Site", related_name="User", through="user_site",
                                   description="用户收藏的景点")
    conversations = fields.ReverseRelation["Conversation"]


class Strategy(Model):
    id = fields.IntField(pk=True, max_length=11)
    strategy = fields.CharField(max_length=2048, description="攻略，日期加地点")
    user = fields.ForeignKeyField("models.User", related_name="strategy", on_delete=fields.SET_NULL, null=True)


class Site(Model):
    id = fields.IntField(pk=True, max_length=11)
    name = fields.CharField(max_length=20, description="景点名字")
    city = fields.CharField(max_length=20, description="城市")
    description = fields.CharField(max_length=1000, description="景点描述")
    picture = fields.CharField(max_length=40, description="景点图片", default="static/site/默认图片.png")
    location = fields.CharField(max_length=40, description="景点地址")
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, description="经度", default=None)
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, description="纬度", default=None)
    users = fields.ManyToManyField("models.User", related_name="Site", through="user_site",
                                   description="喜欢该景点的用户")


class Conversation(Model):
    id = fields.IntField(pk=True, max_length=11)
    content = fields.CharField(max_length=10000, description="历史对话")
    user = fields.ForeignKeyField("models.User", related_name="conversations", on_delete=fields.SET_NULL, null=True)





