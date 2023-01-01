"""
Oauth2 module
"""
from datetime import datetime
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
ALGORITHM: str = 'HS256'


# TODO: Check Jose (JWT) Exceptions
# JWTClaimsError, ExpiredSignatureError


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
            token=token, key=setting.secret_key, algorithms=[ALGORITHM],
            options={"verify_subject": False},
            audience=setting.base_url + '/authentication/login',
            issuer=setting.base_url)
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
