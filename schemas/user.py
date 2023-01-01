"""
User schema for Pydantic models
"""
from datetime import date
from typing import Optional
from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr, Field

from helper.helper import password_regex
from models.gender import Gender
from schemas import CommonUserToken, EditableData


class UserPostRelated(BaseModel):
    """
    UserPostRelated class for PostDisplay class based on Pydantic Base Model
    """
    username: str = Field(
        ..., title='Username', description='Name of the User', min_length=1,
        max_length=50, unique=True)

    class Config:
        """
        Config class for User PostCreate Related
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "username",
            }
        }


class UserDisplay(UserPostRelated):
    """
    UserDisplay class for Response based on User PostCreate Related
    """
    email: EmailStr = Field(
        ..., title='Email', description='Preferred e-mail address of the User',
        unique=True)

    class Config:
        """
        Config class for UserDisplay
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
            }
        }


class UserAuth(UserDisplay):
    """
    UserAuth class for authentication based on User Display
    """
    id: PydanticObjectId = Field(
        ..., title='ID', description='ID of the User', unique=True)

    class Config:
        """
        Config class for User Auth
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "id": "63acf6abf7c607f5429dd304",
                "username": "username",
                "email": "example@mail.com",
            }
        }


class AdditionalEditable(BaseModel):
    """
    Additional editable fields for User and Token classes based on
     Pydantic Base Model.
    """
    city: Optional[str] = Field(
        default=None, title='City', description='City for address of the User')
    state: Optional[str] = Field(
        default=None, title='State',
        description='State for address of the User')
    country: Optional[str] = Field(
        default=None, title='Country',
        description='Country for address of the User')


class UserMe(AdditionalEditable, CommonUserToken, UserDisplay):
    """
    Self User class based on Additional Editable,  Common User-Token
     and User Display.
    """

    class Config:
        """
        Config class for UserMe
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "given_name": "Some",
                "middle_name": "One",
                "family_name": "Example",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "address": "2403 S Bell Blvd",
                "city": "Austin",
                "state": "Texas",
                "country": "United States"
            }
        }


class UserCreate(AdditionalEditable,
                 CommonUserToken, UserDisplay):
    """
    User class for Request based on User Display and Common User-Token.
    """
    password: str = Field(
        ..., title='Password', description='Password of the User',
        min_length=8, max_length=14, regex=password_regex)

    class Config:
        """
        Config class for User Create
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "username",
                "email": "example@mail.com",
                "given_name": "Some",
                "middle_name": "One",
                "family_name": "Example",
                "password": "Hk7pH9*35Fu&3U",
                "gender": Gender.MALE,
                "birthdate": date(2004, 1, 1),
                "phone_number": "+593987654321",
                "address": "2403 S Bell Blvd",
                "city": "Austin",
                "state": "Texas",
                "country": "United States"
            }
        }


class UserUpdate(AdditionalEditable, EditableData, UserDisplay):
    """
    User Update class for Update request based on User PostCreate Related.
    """
    password: Optional[str] = Field(
        title='New password', description='New password of the User',
        min_length=8, max_length=14, regex=password_regex)

    class Config:
        """
        Config class for UserUpdate
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "new_username",
                "email": "new_example@mail.com",
                "phone_number": "+593987654321",
                "address": "2403 S Bell Blvd",
                "city": "Austin",
                "state": "Texas",
                "country": "United States",
                "password": "NewPassword1-"
            }
        }
