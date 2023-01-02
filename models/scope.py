"""
Scope script
"""
from enum import Enum


class Scope(str, Enum):
    """
    Scope class based on Enum
    """
    ACCESS_TOKEN: str = 'access_token'
    REFRESH_TOKEN: str = 'refresh_token'
