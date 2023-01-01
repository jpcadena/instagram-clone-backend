"""
Message schema
"""
from abc import abstractmethod, ABC
from pydantic import BaseModel, Field


class AbstractMsg(ABC):
    """
    Msg based on Abstract Base Class.
    """

    @abstractmethod
    def __init__(self, msg: str) -> None:
        self._msg: str = msg

    @property
    @abstractmethod
    def msg(self) -> None:
        """
        Abstract property msg.
        :return: None
        :rtype: NoneType
        """

    @msg.setter
    @abstractmethod
    def msg(self, value: str):
        pass


class ConcreteMsg(AbstractMsg):
    """
    Concrete Message class based on AbstractMsg.
    """

    def __init__(self, msg: str):
        self._msg: str = msg

    @property
    def msg(self) -> str:
        return self.msg

    @msg.setter
    def msg(self, msg: str) -> None:
        self.msg: str = msg


class BaseMsg(BaseModel):
    """
    Base Msg class based on Pydantic Base Model.
    """

    msg: str = Field(..., title='Message', description='Message response')

    class Config:
        """
        Config class for Msg
        """
        schema_extra: dict[str, dict[str, str]] = {
            "example": {
                "msg": "This is a confirmation message."
            }
        }


class Msg(BaseMsg, ConcreteMsg):
    """
    Msg for Response that inherits from BaseMsg (Pydantic Base Model) and
     ConcreteMsg (Abstract Base Class).
    """

    def __init__(self, msg: str, *args, **kwargs):
        super().__init__(msg=msg, *args, **kwargs)
        self.msg: str = msg
