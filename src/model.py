from tortoise import fields
from tortoise.models import Model
from tortoise.exceptions import ValidationError


class User(Model):
    id = fields.IntField(pk=True, max_length=11)
    number = fields.CharField(max_length=11, description="电话号码")
    password = fields.CharField(max_length=11,description="密码")
    avatar = fields.CharField(max_length=255, description="头像", default="static/默认头像.png")


