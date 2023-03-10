"""
Authentication module
"""
import time
import uuid
from datetime import datetime
from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from fastapi.background import BackgroundTasks
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import EmailStr, ValidationError
from api.deps import get_current_user, redis_dependency, decode_token
from core import config
from core.security import verify_password, create_access_token, \
    create_refresh_token
from crud.user import UsernameSpecification, UsernameFilter
from helper.helper import generate_password_reset_token, \
    send_reset_password_email, verify_password_reset_token
from models.token import Token
from models.user import User
from schemas.msg import Msg
from schemas.token import TokenResponse, TokenResetPassword, TokenPayload
from schemas.user import UserDisplay, UserAuth
from services.authentication import AuthService
from services.token import TokenService
from services.user import UserService

router: APIRouter = APIRouter(
    prefix='/auth', tags=['auth'])


@router.post('/login', response_model=TokenResponse)
async def login(
        user: OAuth2PasswordRequestForm = Depends(),
        setting: config.Settings = Depends(config.get_setting),
        redis: Redis = Depends(redis_dependency)) -> dict:
    """
    Login with OAuth2 authentication using request form.
    - :param user: Object from request body with username and password
     as DI
    - :type user: OAuth2PasswordRequestForm
    - :return: Token information with access token, its type and
     refresh token
    - :rtype: dict
    \f
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :param redis: Dependency method for async redis connection
    :type redis: Redis
    """
    username: str = user.username
    specification: UsernameSpecification = UsernameSpecification(username)
    query: UsernameFilter = UsernameFilter()
    found_user: User = await query.filter(specification)
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Invalid credentials')
    if not await verify_password(found_user.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Incorrect password')
    jti: uuid.UUID = uuid.uuid4()
    payload: dict = {
        "iss": setting.SERVER_HOST, "sub": "username:" + str(found_user.id),
        "aud": setting.SERVER_HOST + '/authentication/login',
        "exp": int(time.time()) + setting.ACCESS_TOKEN_EXPIRE_MINUTES,
        "nbf": int(time.time()) - 1, "iat": int(time.time()),
        "jti": jti,
        "given_name": found_user.given_name,
        "family_name": found_user.family_name,
        "nickname": found_user.given_name,
        "preferred_username": found_user.username, "email": found_user.email,
        "gender": found_user.gender.value, "birthdate": found_user.birthdate,
        "phone_number": found_user.phone_number, "address": found_user.address,
        "updated_at": found_user.updated_at}
    if found_user.middle_name:
        payload["middle_name"] = found_user.middle_name
        first_names: str = found_user.given_name + ' ' + found_user.middle_name
        payload["name"] = first_names + ' ' + found_user.family_name
    access_token: str = await create_access_token(
        payload=payload, setting=setting)
    refresh_token_created: str = await create_refresh_token(
        payload=payload, setting=setting)
    name: str = str(found_user.id) + ':' + str(jti)
    token: Token = Token(key=name, token=refresh_token_created)
    token_set: bool = await TokenService.create_token(token, setting, redis)
    if not token_set:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Could not insert data in Authorization database')
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token_created
    }


@router.get('/refresh_token', status_code=status.HTTP_201_CREATED)
async def refresh_token(
        token: str = Query(
            ..., title='Refresh Token',
            description='Refresh Token to generate a new access token',
            example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'),
        setting: config.Settings = Depends(config.get_setting),
        redis: Redis = Depends(redis_dependency)) -> dict:
    """
    Generate new access token based on given refresh token.
    - :param token: Refresh token to generate a new access token
    - :type token: str
    - :return: New access token for the user
    - :rtype: dict
    \f
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    :param redis: Dependency method for async redis connection
    :type redis: Redis
    """
    credentials_exception: HTTPException = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    current_payload = await decode_token(token, setting)
    current_username: str = current_payload['sub'].replace('username:', '')
    current_jti: str = current_payload['jti']
    key: str = current_username + ':' + current_jti
    value: str = await TokenService.get_token(key, redis)
    if not value:
        raise credentials_exception
    try:
        payload: dict = jwt.decode(
            token=value, key=setting.SECRET_KEY,
            algorithms=[setting.ALGORITHM], options={"verify_subject": False},
            audience=setting.SERVER_HOST + '/authentication/login',
            issuer=setting.SERVER_HOST)
        token_data: TokenPayload = TokenPayload(**payload)
        jti: str = str(token_data.jti)
        if current_jti != jti:
            raise credentials_exception
        if not token_data.preferred_username:
            raise credentials_exception
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        new_token: str = await create_access_token(
            payload=payload, setting=setting)
        return {'access_token': new_token}
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


@router.post("/password-recovery-by-email", response_model=Msg)
async def recover_password_by_email(
        background_tasks: BackgroundTasks,
        email: EmailStr = Query(
            ..., title='Email',
            description='Email to recover password',
            example='email@example.com'),
        setting: config.Settings = Depends(config.get_setting)
) -> dict[str, str]:
    """
    Password Recovery method by e-mail.
    - :param email: Query parameter of Email to recover password from User
    - :type email: EmailStr
    - :return: Confirmation message for email sent
    - :rtype: dict
    \f
    :param background_tasks: Send email to confirm recovery
    :type background_tasks: BackgroundTasks
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    found_user: UserDisplay = await UserService.read_user_by_email(email)
    if not found_user:
        raise HTTPException(
            status_code=404,
            detail=f"The user with this email {email} does not exist in "
                   f"the system.",
        )
    password_reset_token = await generate_password_reset_token(
        email=found_user.email, setting=setting)
    background_tasks.add_task(
        send_reset_password_email, email_to=found_user.email,
        email=found_user.username, token=password_reset_token, setting=setting)
    return {"msg": "Password recovery email sent"}


@router.post("/password-recovery-by-username", response_model=Msg)
async def recover_password_by_username(
        background_tasks: BackgroundTasks,
        username: str = Query(
            ..., title='Username',
            description='Username to recover password', example='username'),
        setting: config.Settings = Depends(config.get_setting)
) -> dict[str, str]:
    """
    Password Recovery method by username.
    - :param username: Query parameter of Username to recover password
     from User
    - :type user: str
    - :return: Confirmation message for email sent
    - :rtype: dict
    \f
    :param background_tasks: Send email to confirm recovery
    :type background_tasks: BackgroundTasks
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    found_user: UserDisplay = await UserService.read_user_by_username(username)
    if not found_user:
        raise HTTPException(
            status_code=404,
            detail=f"The user with this username {username} does not exist in "
                   f"the system.",
        )
    password_reset_token = await generate_password_reset_token(
        email=found_user.email, setting=setting)
    background_tasks.add_task(
        send_reset_password_email, email_to=found_user.email,
        email=found_user.username, token=password_reset_token, setting=setting)
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password", response_model=Msg)
async def reset_password(
        data: TokenResetPassword = Body(
            ..., title='Token and new password',
            description='Token and new password to reset'),
        setting: config.Settings = Depends(config.get_setting)
) -> dict[str, str]:
    """
    Reset password method.
    - :param data: Body Object with token and new password to reset
    - :type token: TokenResetPassword
    - :return: Confirmation message for password changed
    - :rtype: dict
    \f
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    email = await verify_password_reset_token(data.token, setting=setting)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    found_user: User = await AuthService.update_password(email, data.password)
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found in the system.')
    return {"msg": "Password updated successfully"}


@router.post("/logout", status_code=status.HTTP_302_FOUND,
             response_class=RedirectResponse)
async def logout(
        request: Request,
        current_user: UserAuth = Depends(get_current_user)
) -> RedirectResponse:
    """
    Log out method.
    - :return: Response to redirect to homepage
    - :rtype: RedirectResponse
    \f
    :param request: Request to log out from user
    :type request: Request
    :param current_user: Authentication dependency from auth user
    :type current_user: UserAuth
    """
    response: RedirectResponse = RedirectResponse(
        url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key='bearer')
    return response
