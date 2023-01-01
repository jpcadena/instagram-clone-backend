"""
Gender script
"""
from enum import Enum


class Gender(str, Enum):
    """
    Gender class based on Enum
    """
    MALE: str = 'male'
    FEMALE: str = 'female'
    OTHER: str = 'other'
