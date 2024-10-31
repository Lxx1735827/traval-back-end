from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator
from src.model import *

class MapRequest(BaseModel):
    longitude: float
    latitude: float
    scope: int

UserSchema = pydantic_model_creator(User, name="User", exclude_readonly=True)
SiteSchema = pydantic_model_creator(Site, name="Site", exclude_readonly=True)
RestaurantSchema = pydantic_model_creator(Restaurant, name="Restaurant", exclude_readonly=True)
ConversationSchema = pydantic_model_creator(Conversation, name="Conversation", exclude_readonly=True)
ReviewSchema = pydantic_model_creator(Review, name="Review", exclude_readonly=True)
# MapRequestSchema = pydantic_model_creator(MapRequest, name="MapRequest", exclude_readonly=True)
