from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import ValidationError


class User(Model):
    id = fields.IntField(pk=True, max_length=11)
    number = fields.CharField(max_length=11, description="电话号码")
    username = fields.CharField(max_length=20, description="用户名", default="username")
    password = fields.CharField(max_length=11, description="密码")
    avatar = fields.CharField(max_length=255, description="头像", default="static/默认头像.png")



class Strategy(Model):
    id = fields.IntField(pk=True, max_length=11)
    strategy = fields.CharField(max_length=2048, description="攻略，日期加地点")
    # user = fields.ForeignKeyField("src.model.User", related_name="strategy", on_delete=fields.SET_NULL)


class Site(Model):
    id = fields.IntField(pk=True, max_length=11)
    name = fields.CharField(max_length=20, description="景点名字")
    city = fields.CharField(max_length=20, description="城市")
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, description="经度")
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, description="纬度")
