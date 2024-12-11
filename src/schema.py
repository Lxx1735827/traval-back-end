from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, condecimal
from typing import List
from src.model import *

UserSchema = pydantic_model_creator(User, name="User", exclude_readonly=True)
SiteSchema = pydantic_model_creator(Site, name="Site", exclude_readonly=True)
RestaurantSchema = pydantic_model_creator(Restaurant, name="Restaurant", exclude_readonly=True)
ConversationSchema = pydantic_model_creator(Conversation, name="Conversation", exclude_readonly=True)
ReviewSchema = pydantic_model_creator(Review, name="Review", exclude_readonly=True)
TextSchema = pydantic_model_creator(Text, name="Text", exclude_readonly=True)

class Point(BaseModel):
    name: str
    latitude: condecimal(max_digits=9, decimal_places=6)
    longitude: condecimal(max_digits=9, decimal_places=6)


class NewSiteSchema(BaseModel):
    id: int
    name: str
    location: str
    picture: str
    latitude: condecimal(max_digits=9, decimal_places=6)
    longitude: condecimal(max_digits=9, decimal_places=6)


class DayRouteSchema(BaseModel):
    start_point: Point
    end_point: Point
    sites: List[NewSiteSchema]
