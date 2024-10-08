from tortoise.contrib.pydantic import pydantic_model_creator
from src.model import *

UserSchema = pydantic_model_creator(User, name="User", exclude_readonly=True)