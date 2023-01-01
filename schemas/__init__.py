"""
Schemas module
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, PastDate
from helper.helper import TELEPHONE_REGEX
from models.gender import Gender


class EditableData(BaseModel):
    """
    Editable fields for User and Token classes based on Pydantic
     Base Model.
    """
    phone_number: Optional[str] = Field(
        default=None, title='Telephone',
        description='Preferred telephone number of the User',
        regex=TELEPHONE_REGEX)
    address: Optional[str] = Field(
        default=None, title='Address',
        description='Preferred postal address of the User')


class CommonUserToken(EditableData):
    """
    Common fields for User and Token classes based on EditableData.
    """
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
    updated_at: Optional[datetime] = Field(
        default=None, title='Updated at',
        description='Time the User information was last updated')
