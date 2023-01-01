"""
Authentication Service.
"""
from pydantic import EmailStr
from core.security import get_password_hash
from db.db import handle_nosql_exceptions
from models.user import User


class AuthService:
    """
    User services for database
    """

    @staticmethod
    @handle_nosql_exceptions
    async def update_password(email: EmailStr, password: str) -> User:
        """
        Update user password in database given its e-mail
        :param email: Email from User document
        :type email: EmailStr
        :param password: New password to update
        :type password: str
        :return: User updated from database
        :rtype: User
        """
        user_to_update: User = await User.find_one(User.email == email)
        hashed_password: str = await get_password_hash(password)
        await user_to_update.update(
            {"$set": {User.password: hashed_password}},
            skip_actions=['hash_password'])
        return user_to_update
