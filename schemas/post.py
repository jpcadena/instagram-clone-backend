"""
PostCreate schema for Pydantic models
"""
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class PostCreate(BaseModel):
    """
    PostCreate class based on Pydantic Base Model.
    """
    image_url: HttpUrl = Field(
        ..., title='Post image URL', description='URL of the Post image')
    caption: str = Field(
        ..., title='Post caption', description='Caption of the Post',
        min_length=1, max_length=2200)

    class Config:
        """
        Config class for PostCreate Base.
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "image_url": "https://imgur.com/",
                "caption": "My caption"
            }
        }


class PostDisplay(PostCreate):
    """
    PostDisplay class based on Post Create.
    """
    created_at: datetime = Field(
        default=datetime.now(), title='Created at',
        description='Timestamp for creation of the PostCreate')

    # comments_link: Optional[list[Comment]] = Field(
    #     title='Comments list',
    #     description='List of comments in current Post', unique_items=True)

    class Config:
        """
        Config class for PostDisplay.
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "image_url": "https://imgur.com/",
                "caption": "My caption",
                "created_at": datetime.utcnow(),
                # "comments_link": [Comment(), ]
            }
        }


class Post(PostDisplay):
    """
    Post class to display based on Post Display.
    """
    post_owner: str = Field(
        ..., title='Owner username',
        description='Username of the user who created the post')

    class Config:
        """
        Config class for Post.
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "id": '63aefa38afda3a176c1e3562',
                "image_url": "https://imgur.com/",
                "caption": "My caption",
                "created_at": datetime.utcnow(),
                # "comments": [
                #     Comment(),],
                "post_owner": 'username',
            }
        }
