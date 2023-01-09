"""
Oauth2 module
"""
from abc import ABC
from datetime import datetime
from typing import Optional
from aioredis import Redis
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from core import config
from models.user import User
from schemas.token import TokenPayload
from schemas.user import UserAuth
from services.user import UserService

oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(
    tokenUrl="/authentication/login", scheme_name="JWT")


async def decode_token(
        token: str, setting: config.Settings = Depends(config.get_setting)
) -> Optional[dict]:
    """
    Decode a token with OAuth2
    :param token: Given token to decode
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: Payload with JWT claims
    :rtype: dict
    """
    payload: dict
    try:
        payload = jwt.decode(
            token=token, key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM], options={"verify_subject": False},
            audience=setting.SERVER_HOST + '/authentication/login',
            issuer=setting.SERVER_HOST)
        return payload
    except jwt.ExpiredSignatureError as es_exc:
        print(es_exc, ' - ', 'Token expired')
        return None
    except jwt.JWTClaimsError as c_exc:
        print(c_exc, ' - ', 'Authorization claim is incorrect, '
                            'please check audience and issuer')
        return None
    except jwt.JWTError as exc:
        print(exc)
        return None


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        setting: config.Settings = Depends(config.get_setting)
) -> UserAuth:
    """
    Function to get current user
    :param token: access token from OAuth2PasswordBearer
    :type token: str
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: current user from DB
    :rtype: UserAuth
    """
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: dict = jwt.decode(
            token=token, key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM], options={"verify_subject": False},
            audience=setting.SERVER_HOST + '/authentication/login',
            issuer=setting.SERVER_HOST)
        token_data: TokenPayload = TokenPayload(**payload)
        username: str = payload.get("preferred_username")
        if username is None:
            raise credentials_exception
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.ExpiredSignatureError as es_exc:
        raise HTTPException(
            status_code=401, detail='Token expired') from es_exc
    except jwt.JWTClaimsError as c_exc:
        raise HTTPException(
            status_code=401,
            detail='Authorization claim is incorrect, please check'
                   ' audience and issuer') from c_exc
    except (JWTError, ValidationError) as exc:
        raise credentials_exception from exc
    user: User = await UserService.read_user_by_username(username=username)
    if not user:
        raise credentials_exception
    user_dict: dict = user.dict()
    user_auth: UserAuth = UserAuth(
        id=user_dict.get('id'), username=user_dict.get('username'),
        email=user_dict.get('email'))
    return user_auth


class RedisDependency:
    """
    FastAPI Dependency for Redis Connections
    """

    redis: Optional[ABC] = None

    async def __call__(self):
        if self.redis is None:
            await self.init()
        return self.redis

    async def init(self):
        """
        Initialises the Redis Dependency.
        :return: None
        :rtype: NoneType
        """
        setting: config.Settings = config.get_setting()
        url: str = setting.redis_endpoint
        self.redis = await Redis.from_url(url, decode_responses=True)


redis_dependency: RedisDependency = RedisDependency()
