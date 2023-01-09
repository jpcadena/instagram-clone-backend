"""
Hashing module for core package
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt
from core import config

pwd_cxt: CryptContext = CryptContext(
    schemes=['bcrypt'], deprecated='auto')
oauth2_scheme: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="login")


async def create_access_token(
        payload: dict, expires_delta: Optional[timedelta] = None,
        setting: config.Settings = Depends(config.get_setting)) -> str:
    """
    Function to create a new access token
    :param payload: claims for token
    :type payload: dict
    :param expires_delta: time expiration
    :type expires_delta: timedelta
    :return: encoded JWT
    :rtype: str
    """
    expire: datetime
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({'exp': int(expire.timestamp())})
    claims: dict = jsonable_encoder(payload)
    encoded_jwt: str = jwt.encode(claims=claims, key=setting.SECRET_KEY,
                                  algorithm=setting.ALGORITHM)
    return encoded_jwt


async def create_refresh_token(
        payload: dict, setting: config.Settings = Depends(config.get_setting)
) -> str:
    """
    Create refresh token for authentication
    :param payload: data to be used as payload in Token
    :type payload: dict
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :return: access token with refresh expiration time
    :rtype: str
    """
    expires: timedelta = timedelta(
        minutes=setting.REFRESH_TOKEN_EXPIRE_MINUTES)
    return await create_access_token(payload=payload, expires_delta=expires,
                                     setting=setting)


async def get_password_hash(password: str) -> str:
    """
    Bcrypt function for password
    :param password: User password to encrypt
    :type password: str
    :return: Hashed password
    :rtype: str
    """
    return pwd_cxt.hash(secret=password)


async def verify_password(hashed_password, plain_password) -> bool:
    """
    Verify if secret is hashed password
    :param hashed_password: Hash password
    :type hashed_password: str
    :param plain_password: User password
    :type plain_password: str
    :return: If passwords match
    :rtype: bool
    """
    return pwd_cxt.verify(secret=plain_password, hash=hashed_password)
