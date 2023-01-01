"""
CRUD User operations
"""
from pydantic import EmailStr
from crud import Specification, Filter
from models.user import User


class EmailSpecification(Specification):
    """
    Email Specification class based on Specification
    """

    def __init__(self, email: EmailStr):
        super().__init__(email)
        self.email: EmailStr = email


class UsernameSpecification(Specification):
    """
    Username Specification class based on Specification
    """

    def __init__(self, username: str):
        super().__init__(username)
        self.username: str = username


class UserFilter(Filter):
    """
    User Filter class based on Filter for ID.
    """

    async def filter(self, spec: Specification):
        doc: User = await User.get(spec.value)
        return doc


class UsernameFilter(Filter):
    """
    Username Filter class based on Filter.
    """

    async def filter(self, spec: UsernameSpecification):
        username: str = spec.username
        user: User = await User.find_one(User.username == username)
        return user


class EmailFilter(Filter):
    """
    Email Filter class based on Filter.
    """

    async def filter(self, spec: EmailSpecification):
        email: str = spec.email
        user: User = await User.find_one(User.email == email)
        return user


class UsersFilter(Filter):
    """
    Users Filter class based on Filter.
    """

    async def filter(self, spec: Specification = None):
        users: list[User] = await User.find_all().to_list()
        return users
