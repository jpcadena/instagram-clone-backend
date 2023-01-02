"""
Message schema
"""
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, EmailStr, AnyUrl
from core import config
from models.scope import Scope
from schemas import CommonUserToken
from schemas.user import password_regex

sub_regex: str = r'(^username:)[a-z0-9]{24}'


class BasicPublicClaimsToken(CommonUserToken):
    """
    Public Claims Token with email field added based on Common User-Token.
    """

    email: EmailStr = Field(
        ..., title='Email', description='Preferred e-mail address of the User',
        unique=True)


class PublicClaimsToken(BasicPublicClaimsToken):
    """
    Token class based on BasicPublicClaimsToken with Public claims (IANA).
    """

    name: str = Field(
        title='Full name', description='Full name of the User', min_length=1,
        max_length=50)
    nickname: str = Field(
        title='Casual name',
        description='Casual name of the User (First Name)', min_length=1,
        max_length=50)
    preferred_username: str = Field(
        ..., title='Preferred username',
        description='Shorthand name by which the End-User wishes to be '
                    'referred to (Username)', min_length=1, max_length=50,
        unique=True)


class RegisteredClaimsToken(BaseModel):
    """
    Registered Claims Token class based on Pydantic Base Model with
    Registered claims.
    """

    iss: AnyUrl = Field(
        default=config.get_setting().base_url, title='Issuer',
        description='Principal that issued JWT as HTTP URL')
    sub: str = Field(
        ..., title='Subject',
        description="Subject of JWT starting with 'username:' followed by"
                    " User ID", min_length=1, regex=sub_regex)
    aud: str = Field(
        default=config.get_setting().auth_path, title='Audience',
        description='Recipient of JWT', const=True, min_length=1)
    exp: int = Field(
        ..., title='Expiration time',
        description="Expiration time on or after which the JWT MUST NOT be"
                    " accepted for processing", gt=1)
    nbf: int = Field(
        ..., title='Not Before',
        description="Time Before which the JWT MUST NOT be accepted for "
                    "processing", gt=1)
    iat: int = Field(
        ..., title='Issued At',
        description="Time at which the JWT was issued", gt=1)
    jti: UUID = Field(
        default_factory=uuid4, title='JWT ID',
        description="Unique Identifier for the JWT", unique=True)
    scope: Scope = Field(default=Scope.ACCESS_TOKEN, title='Scope',
                         description='Scope value')


class TokenPayload(PublicClaimsToken, RegisteredClaimsToken):
    """
    Token Payload class based on RegisteredClaimsToken and PublicClaimsToken.
    """

    @classmethod
    def get_field_names(cls, alias: bool = False) -> list:
        """
        Retrieve the class attributes as a list.
        :param alias: Check for alias in the schema
        :type alias: bool
        :return: class attributes
        :rtype: list
        """
        return list(cls.schema(alias).get("properties").keys())

    class Config:
        """
        Config class for Token Payload
        """
        schema_extra: dict[str, dict] = {
            "example": {
                'iss': 'http://localhost:8000',
                'sub': 'username:63aefa38afda3a176c1e3562',
                'aud': 'http://localhost:8000/authentication/login',
                'exp': 1672433102, 'nbf': 1672413301, 'iat': 1672413302,
                'jti': 'ce0f27c1-c559-45b1-b016-a81a600af197',
                'scope': 'access_token',
                'given_name': 'Juan', 'family_name': 'Cadena Aguilar',
                'nickname': 'Juan', 'preferred_username': 'jpcadena',
                'email': 'jpcadena@espol.edu.ec', 'gender': 'male',
                'birthdate': '1993-08-24', 'phone_number': '+593987654321',
                'address': '2403 S Bell Blvd', 'updated_at': None,
                'middle_name': 'Pablo', 'name': 'Juan Pablo Cadena Aguilar'
            }
        }


class TokenResponse(BaseModel):
    """
    Token for Response based on Pydantic Base Model.
    """
    access_token: str = Field(
        ..., title='Token', description='Access token')
    token_type: str = Field(
        ..., title='Token type', description='Type of the token')
    refresh_token: str = Field(
        ..., title='Refresh Token', description='Refresh token')

    class Config:
        """
        Config class for TokenResponse
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                                "eyJleHAiOjE2NzA4MTg0NDUsImlzcyI6Imh0dHBzOi8v"
                                "d3d3Lmluc3RhZ3JhbWNsb25lLmNvbSIsInN1YiI6MSwi"
                                "ZW1haWwiOiJqcGNhZGVuYUBlc3BvbC5lZHUuZWMiLCJp"
                                "YXQiOjE2NzA4MTQ1NDUsInByZWZlcnJlZF91c2VybmFt"
                                "ZSI6ImpwY2FkZW5hIiwidXBkYXRlZF9hdCI6bnVsbH0."
                                "STF4EOTtyO81lKNR4H36G7l2uRuUBfFvfuKUd4CMqJM",
                "token_type": "bearer",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                                 "eyJleHAiOjE2NzA4MTg0NDUsImlzcyI6Imh0dHBzOi8v"
                                 "d3d3Lmluc3RhZ3JhbWNsb25lLmNvbSIsInN1YiI6MSwi"
                                 "ZW1haWwiOiJqcGNhZGVuYUBlc3BvbC5lZHUuZWMiLCJp"
                                 "YXQiOjE2NzA4MTQ1NDUsInByZWZlcnJlZF91c2VybmFt"
                                 "ZSI6ImpwY2FkZW5hIiwidXBkYXRlZF9hdCI6bnVsbH0."
                                 "STF4EOTtyO81lKNR4H36G7l2uRuUBfFvfuKUd4CMqJM",
            }
        }


class TokenResetPassword(BaseModel):
    """
    Token Reset Password for Request based on Pydantic Base Model.
    """
    token: str = Field(
        ..., title='Token', description='Access token')
    password: str = Field(
        ..., title='New password', description='New password to reset',
        min_length=8, max_length=14, regex=password_regex)

    class Config:
        """
        Config class for Token Reset Password
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
                         "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gR"
                         "G9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2"
                         "QT4fwpMeJf36POk6yJV_adQssw5c",
                "password": "Hk7pH9*35Fu&3U"
            }
        }
