"""
User DB Model module
"""
from datetime import datetime
from typing import Optional
from beanie import Document, Indexed, before_event, Insert, Update, Replace
from pydantic import EmailStr, Field, PastDate
from core.security import get_password_hash
from helper.helper import TELEPHONE_REGEX
from models.gender import Gender


# TODO: For State and Country check: https://unece.org/trade/uncefact/unlocode


class User(Document):
    """
    User Class based on Beanie Document (MongoDB) and UserCreate Schema.
    """
    username: Indexed(str, unique=True) = Field(
        ..., title='Username', description='Name of the User', min_length=1,
        max_length=50, unique=True, index=True)
    email: Indexed(EmailStr, unique=True) = Field(
        ..., title='Email', description='Preferred e-mail address of the User',
        unique=True)
    password: str = Field(
        ..., title='Hashed password',
        description='Hashed password of the User')
    given_name: str = Field(
        title='First name',
        description='Given name(s) or first name(s) of the User', min_length=1,
        max_length=50)
    family_name: str = Field(
        title='Last name',
        description='Surname(s) or last name(s) of the User', min_length=1,
        max_length=50)
    middle_name: Optional[str] = Field(
        title='Middle name', description='Middle name(s) of the User',
        max_length=50)
    gender: Optional[Gender] = Field(
        default=Gender.MALE, title='Gender', description='Gender of the User')
    birthdate: Optional[PastDate] = Field(
        default=None, title='Birthdate', description='Birthday of the User')
    phone_number: Optional[str] = Field(
        default=None, title='Telephone',
        description='Preferred telephone number of the User',
        regex=TELEPHONE_REGEX)
    address: Optional[str] = Field(
        default=None, title='Address',
        description='Preferred postal address of the User')
    updated_at: Optional[datetime] = Field(
        default=None, title='Updated at',
        description='Time the User information was last updated')
    city: Optional[str] = Field(
        default=None, title='City', description='City for address of the User')
    state: Optional[str] = Field(
        default=None, title='State',
        description='State for address of the User')
    country: Optional[str] = Field(
        default=None, title='Country',
        description='Country for address of the User')
    is_active: Optional[bool] = Field(
        default=True, title='Is active?',
        description='True if the user is active; otherwise false')
    created_at: Optional[datetime] = Field(
        default=None, title='Created at',
        description='Time the User was created')

    @before_event(Insert)
    async def pastdate_to_datetime(self) -> None:
        """
        Before database Insert event to cast birthdate attribute from
        PastDate to datetime
        :return: None
        :rtype: NoneType
        """
        self.birthdate: datetime = datetime.combine(
            self.birthdate, datetime.min.time())

    @before_event(Insert, Update, Replace)
    async def hash_password(self) -> None:
        """
        Before database Insert event to hash password
        :return: None
        :rtype: NoneType
        """
        temp_pass: str = self.password
        self.password: str = await get_password_hash(temp_pass)

    @before_event(Insert)
    async def set_created_at(self) -> None:
        """
        Before database Insert event to set created_at attribute as now
        :return: None
        :rtype: NoneType
        """
        self.created_at: datetime = datetime.now()

    @before_event([Update, Replace])
    async def set_updated_at(self) -> None:
        """
        Before database Update and Replace events to set updated_at
         attribute as now
        :return: None
        :rtype: NoneType
        """
        self.updated_at: datetime = datetime.utcnow()

    class Settings:
        """
        Document settings for User.
        """
        name: str = "users"
        validate_on_save: bool = True

    class Config:
        """
        Config Class for User document
        """
        schema_extra: dict[str, dict] = {
            "example": {
                "username": "someone",
                "email": "someone@example.com",
                "given_name": "Some",
                "middle_name": "One",
                "family_name": "Example",
                "password": "5994471abb01112afcc18159f6cc74b4f511b99806da59b"
                            "3caf5a9c173cacfc5",
                "gender": Gender.MALE,
                "birthdate": datetime(2004, 1, 1),
                "phone_number": "+593987654321",
                "address": "2403 S Bell Blvd",
                "city": "Austin",
                "state": "Texas",
                "country": "United States",
                "is_active": True,
                "created_at": datetime(2022, 12, 28, 23, 55, 59, 342380),
                "updated_at": datetime.now()
            }
        }
