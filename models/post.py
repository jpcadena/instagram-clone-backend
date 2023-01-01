"""
PostCreate DB Model module
"""
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field
from schemas.post import PostDisplay


class Post(Document, PostDisplay):
    """
    Post Class for database based on Beanie Document (MongoDB) and Post Schema.
    """
    user_id: PydanticObjectId = Field(
        ..., title='User ID',
        description='ID of the User who created the post',
        foreign_key='user.id')

    class Settings:
        """
        Document settings for Post.
        """
        name: str = "posts"
        validate_on_save: bool = True

    class Config:
        """
        Config Class for Post document
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "id": '63aefa38afda3a176c1e3562',
                "image_url": "https://imgur.com/",
                "caption": "My caption",
                "created_at": datetime.utcnow(),
                # "comments": [
                #     Comment(), ],
                "user_id": '63aefa38afda3a176c1e3526',
            }
        }
