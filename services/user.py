"""
User Service
"""
from datetime import datetime
from typing import Optional, Union
from beanie import PydanticObjectId
from pydantic import EmailStr
from pymongo.errors import DuplicateKeyError
from crud import IdSpecification
from crud.user import EmailSpecification, EmailFilter, UserFilter, \
    UsersFilter, UsernameSpecification, UsernameFilter
from db.db import handle_nosql_exceptions
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserService:
    """
    User services for database
    """

    @staticmethod
    @handle_nosql_exceptions
    async def create_user(user: UserCreate) -> Union[User, str]:
        """
        Create user in database
        :param user: User from HTTP Request
        :type user: UserCreate
        :return: User from database
        :rtype: User
        """
        user_in: User = User(**user.dict())
        try:
            user_inserted: User = await user_in.insert()
        except DuplicateKeyError as dk_exc:
            key: str = list(dk_exc.details.get('keyValue').keys())[0]
            print(key)
            return key
        return user_inserted

    @staticmethod
    @handle_nosql_exceptions
    async def read_user_by_id(user_id: PydanticObjectId) -> Optional[User]:
        """
        Get user from database by ID
        :param user_id: Identifier from User document
        :type user_id: PydanticObjectId
        :return: User from database
        :rtype: User
        """
        id_specification: IdSpecification = IdSpecification(user_id)
        query: UserFilter = UserFilter()
        user: User = await query.filter(id_specification)
        return user

    @staticmethod
    @handle_nosql_exceptions
    async def read_users() -> Optional[list[User]]:
        """
        Get users from database
        :return: Users from database
        :rtype: list[User]
        """
        query: UsersFilter = UsersFilter()
        users: list[User] = await query.filter()
        return users

    @staticmethod
    @handle_nosql_exceptions
    async def read_user_by_email(email: EmailStr) -> User:
        """
        Get user from database by its email
        :param email: filter to use
        :type email: EmailStr
        :return: User from database
        :rtype: User
        """
        specification: EmailSpecification = EmailSpecification(email)
        query: EmailFilter = EmailFilter()
        user: User = await query.filter(specification)
        return user

    @staticmethod
    @handle_nosql_exceptions
    async def read_user_by_username(username: str) -> User:
        """
        Get user from database by its username
        :param username: filter to use
        :type username: str
        :return: User from database
        :rtype: User
        """
        specification: UsernameSpecification = UsernameSpecification(username)
        query: UsernameFilter = UsernameFilter()
        user: User = await query.filter(specification)
        return user

    @staticmethod
    @handle_nosql_exceptions
    async def update_user(user_id: PydanticObjectId, data: UserUpdate) -> User:
        """
        Update user information in database given its ID
        :param user_id: Identifier from User document
        :type user_id: PydanticObjectId
        :param data: Information to update from the User
        :type data: UserUpdate
        :return: User updated from database
        :rtype: User
        """
        user_updated: User = await User.get(user_id)
        skip_actions: list[str] = None
        if not data.password:
            skip_actions = ['hash_password']
        await user_updated.update(
            {"$set": data.dict(exclude_unset=True)}, skip_actions=skip_actions)
        return user_updated

    @staticmethod
    @handle_nosql_exceptions
    async def delete_user(user_id: PydanticObjectId) -> dict:
        """
        Delete User in database given its ID
        :param user_id: Identifier from User document
        :type user_id: PydanticObjectId
        :return: Data to confirmation info about the delete process
        :rtype: dict
        """
        deleted: bool = True
        found_user: User = await User.get(user_id)
        if not found_user:
            deleted = False
        else:
            await found_user.delete()
        return {"ok": deleted, 'deleted_at': datetime.now()}
