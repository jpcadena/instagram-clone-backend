"""
PostCreate services script.
"""
from datetime import datetime
from typing import Optional, Union
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from crud import IdSpecification
from crud.post import PostFilter, PostsFilter
from db.db import handle_nosql_exceptions
from models.post import Post
from models.user import User
from schemas.post import PostCreate
from services.user import UserService


class PostService:
    """
    PostCreate services for database.
    """

    @staticmethod
    @handle_nosql_exceptions
    async def create_post(
            post: PostCreate, user_id: PydanticObjectId) -> Union[Post, str]:
        """
        Create a new post into the database
        :param post: Post with image_url and caption
        :type post: PostCreate
        :param user_id: User ID
        :type user_id: PydanticObjectId
        :return: Post with ID, image_url, caption, timestamp for creation,
        user_id and list of comments
        :rtype: PostCreate
        """
        post_owner: User = await UserService.read_user_by_id(user_id)
        post_in: Post = Post(**post.dict(), user_id=post_owner.id)
        try:
            post_inserted: Post = await post_in.insert()
        except DuplicateKeyError as dk_exc:
            key: str = list(dk_exc.details.get('keyValue').keys())[0]
            print(key)
            return key
        return post_inserted

    @staticmethod
    @handle_nosql_exceptions
    async def read_post_by_id(
            post_id: PydanticObjectId) -> Optional[Post]:
        """
        Read Post from database with given ID and User ID
        :param post_id: Identifier of specific Post
        :type post_id: PydanticObjectId
        :return: Post with given id retrieved from database and also includes
         image_url, caption, timestamp for creation, user_id and
         optional relationships
        :rtype: PostCreate
        """
        id_specification: IdSpecification = IdSpecification(post_id)
        query: PostFilter = PostFilter()
        post: Post = await query.filter(id_specification)
        return post

    @staticmethod
    @handle_nosql_exceptions
    async def read_all_posts() -> Optional[list[Post]]:
        """
        Read Posts from current user
        :return: list of Posts with ID, image_url, caption, timestamp for
         creation, user_id and optional relationships from current user
        :rtype: list[PostCreate]
        """
        query: PostsFilter = PostsFilter()
        posts: list[Post] = await query.filter()
        return posts

    @staticmethod
    @handle_nosql_exceptions
    async def delete_post(post_id: PydanticObjectId) -> dict:
        """
        Delete Post in database given its ID
        :param post_id: Identifier from Post document
        :type post_id: PydanticObjectId
        :return: Data to confirmation info about the delete process
        :rtype: dict
        """
        deleted: bool = True
        post: Post = await Post.get(post_id)
        if not post:
            deleted = False
        else:
            await post.delete()
        return {"ok": deleted, 'deleted_at': datetime.now()}
