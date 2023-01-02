"""
Token Service
"""

from aioredis import RedisError, Redis
from fastapi import Depends
from api.deps import redis_dependency
from core import config
from db.authorization import handle_redis_exceptions
from models.token import Token


class TokenService:
    """
    Token services for authorization database
    """

    @staticmethod
    @handle_redis_exceptions
    async def create_token(
            token: Token,
            setting: config.Settings = Depends(config.get_setting),
            redis: Redis = Depends(redis_dependency)) -> bool:
        """
        Create token in authorization database
        :param token: Token object with key and value
        :type token: Token
        :return: True if the token was inserted; otherwise false
        :rtype: bool
        """
        inserted: bool = False
        try:
            inserted = await redis.setex(
                token.key, setting.refresh_token_expire_seconds, token.token)
        except RedisError as r_exc:
            print(r_exc)
        return inserted

    @staticmethod
    @handle_redis_exceptions
    async def get_token(
            key: str,
            redis: Redis = Depends(redis_dependency)) -> str:
        """
        Read token from authorization database
        :param key: key to search for
        :type key: str
        :return: Refresh token
        :rtype: str
        """
        value: str
        try:
            value = await redis.get(key)
        except RedisError as r_exc:
            print(r_exc)
            value = None
        return value
