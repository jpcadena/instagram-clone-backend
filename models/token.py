"""
Token DB Model
"""
from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    Token class based on Pydantic Base Model.
    """
    key: str = Field(..., title='Key',
                     description='Refresh token key based on User ID and JTI')
    token: str = Field(..., title='Token',
                       description='Refresh token retrieved from login')

    class Config:
        """
        Config class for Token.
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                'key': "63aefa38afda3a176c1e3562:ce0f27c1-c559-45b1-b016-"
                       "a81a600af197",
                'token': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                         "eyJleHAiOjE2NzA4MTg0NDUsImlzcyI6Imh0dHBzOi8v"
                         "d3d3Lmluc3RhZ3JhbWNsb25lLmNvbSIsInN1YiI6MSwi"
                         "ZW1haWwiOiJqcGNhZGVuYUBlc3BvbC5lZHUuZWMiLCJp"
                         "YXQiOjE2NzA4MTQ1NDUsInByZWZlcnJlZF91c2VybmFt"
                         "ZSI6ImpwY2FkZW5hIiwidXBkYXRlZF9hdCI6bnVsbH0."
                         "STF4EOTtyO81lKNR4H36G7l2uRuUBfFvfuKUd4CMqJM",
            }
        }
