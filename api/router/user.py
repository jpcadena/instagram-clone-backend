"""
User router module for API endpoints.
"""
from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Path, \
    BackgroundTasks, Body
from fastapi.responses import Response
from api.deps import get_current_user
from core import config
from helper.helper import send_new_account_email
from models.user import User
from schemas.user import UserDisplay, UserCreate, UserAuth, UserUpdate, UserMe
from services.user import UserService

router: APIRouter = APIRouter(prefix='/user', tags=['user'])


@router.post('/register-user', response_model=UserDisplay,
             status_code=status.HTTP_201_CREATED)
async def register_user(
        background_tasks: BackgroundTasks,
        user: UserCreate = Body(..., title='New user',
                                description='New user to register'),
        setting: config.Settings = Depends(config.get_setting)) -> UserDisplay:
    """
    Register new user into the system.
    - :param user: Object with username, email, first name,
    middle name [OPTIONAL], last name, password, gender [OPTIONAL],
    birthdate [OPTIONAL], phone_number [OPTIONAL], address [OPTIONAL],
    city [OPTIONAL], state [OPTIONAL] and country [OPTIONAL].
    - :type user: UserCreate
    - :return: User created with its name and email
    - :rtype: UserDisplay
    \f
    :param background_tasks: Task to be executed on background
    :type background_tasks: BackgroundTasks
    :param setting: Dependency method for cached setting object
    :type setting: Settings
    """
    new_user: UserDisplay = await UserService.create_user(user)
    if isinstance(new_user, str):
        key: str = new_user
        value: str
        if new_user == 'email':
            value = user.email
        else:
            value = user.username
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'User with {key} {value} already exists in the system.')
    if new_user:
        if setting.EMAILS_ENABLED and user.email:
            background_tasks.add_task(send_new_account_email, user.email,
                                      user.username, setting)
    return new_user


@router.get('/get-me', response_model=UserMe)
async def get_me(
        current_user: UserAuth = Depends(get_current_user)) -> UserMe:
    """
    Get current user information from the system.
    - :return: Current User information retrieved
    - :rtype: UserDisplay
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_user: User = await UserService.read_user_by_id(current_user.id)
    user_me: UserMe = UserMe(**found_user.dict())
    return user_me


@router.get('/get-user/{user_id}', response_model=UserDisplay)
async def get_user(
        user_id: PydanticObjectId = Path(
            ..., title='User ID', description='ID of the User to searched',
            example='63aefa38afda3a176c1e3562'),
        current_user: UserAuth = Depends(get_current_user)) -> UserDisplay:
    """
    Get User by ID from .
    - :param user_id: Path parameter as ID of the User to be searched.
    - :type user_id: PydanticObjectId
    - :return: User retrieved from database with username and email
    - :rtype: UserDisplay
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    # found_user: UserCreate = await User.read(user_id)
    found_user: User = await UserService.read_user_by_id(user_id)
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID {user_id} '
                                   f'not found in the system.')
    displayed_user: UserDisplay = UserDisplay(**found_user.dict())
    return displayed_user


@router.get('/get-all-users', response_model=list[UserDisplay])
async def get_users(
        current_user: UserAuth = Depends(get_current_user)
) -> list[UserDisplay]:
    """
    Get all Users from the system.
    - :return: List of Users retrieved from database with username and email
    - :rtype: list[UserDisplay]
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_users: list[UserDisplay] = await UserService.read_users()
    if not found_users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Users not found in the system.')
    return found_users


@router.put('/update-user/{user_id}', response_model=UserDisplay)
async def update_user(user_id: PydanticObjectId = Path(
    ..., title='User ID', description='ID of the User to updated',
    example='63aefa38afda3a176c1e3562'), user: UserUpdate = Body(
    ..., title='User data', description='New user data to update'),
        current_user: UserAuth = Depends(get_current_user)) -> UserDisplay:
    """
    Update user information by its ID into the system.
    - :param user_id: Path parameter as ID of the User to be updated.
    - :type user_id: PydanticObjectId
    - :param user: Body User object with new data to update that includes
     username, email, password [OPTIONAL], gender [OPTIONAL],
      phone_number [OPTIONAL], address [OPTIONAL], city [OPTIONAL],
       state [OPTIONAL] and country [OPTIONAL].
    - :type user: UserUpdate
    - :return: List of Users retrieved from database with username and email
    - :rtype: list[UserDisplay]
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_user: UserCreate = await UserService.update_user(user_id, user)
    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found in the system.')
    displayed_user: UserDisplay = UserDisplay(**found_user.dict())
    return displayed_user


@router.delete('/delete-user/{user_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: PydanticObjectId = Path(
    ..., title='User ID', description='ID of the User to deleted',
    example='63aefa38afda3a176c1e3562'),
        current_user: UserAuth = Depends(get_current_user)) -> Response:
    """
    Delete user by its ID from the system.
    - :param user_id: Path parameter as ID of the User to be deleted.
    - :type user_id: PydanticObjectId
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    data: dict = await UserService.delete_user(user_id)
    response: Response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
        media_type='application/json')
    response.headers['deleted'] = str(data['ok']).lower()
    response.headers['deleted_at'] = str(data['deleted_at'])
    return response
