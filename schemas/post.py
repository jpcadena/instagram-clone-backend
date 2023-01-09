"""
PostCreate schema for Pydantic models
"""
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class PostCreate(BaseModel):
    """
    PostCreate for Request based on Pydantic Base Model.
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
    PostDisplay for Response that inherits from Post Create.
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
    Post for Response that inherits from Post Display.
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

# Instagram:
# media-id
# caption: The Media's caption text. Not returnable for Media in albums.
# id: The Media's ID.
# media_type: The Media's type. Can be IMAGE, VIDEO, or CAROUSEL_ALBUM.
# media_url: The Media's URL.
# permalink: The Media's permanent URL.
# timestamp: The Media's publish date in ISO 8601 format.
# username: The Media owner's username.
# {
#     "data": [],
# }

# user-id: path, access_token: query, fields: query as list
# account_type: The User's account type. Can be BUSINESS,
# MEDIA_CREATOR, or PERSONAL.
# id: The app user's app-scoped ID.
# media_count: The number of Media on the User.
# username: The User's username.

# POST
# access_token: The user's app-scoped short-lived Instagram User Access Token.
# user_id: The user's app-scoped User ID (integer)

# {
#     "access_token": "{access-token}",
#     "user_id": {user - id}
# }

# GET
# "expires_in": {expires-in}
# expires_in: The number of seconds until the long-lived token expires.
# 60 days vs 1 hour

