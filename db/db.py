"""
Main database module (MongoDB)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from pymongo.errors import ExecutionTimeout, DuplicateKeyError, InvalidName, \
    InvalidOperation, NetworkTimeout, NotPrimaryError, OperationFailure, \
    WTimeoutError, WriteError
from core import config
from models.post import Post
from models.user import User


async def init_db() -> None:
    """
    Init connection to MongoDB
    :return: None
    :rtype: NoneType
    """
    setting: config.Settings = config.get_setting()
    connection_string: str = setting.mongo_connection
    client: AsyncIOMotorClient = AsyncIOMotorClient(connection_string)
    database = client.instagramCloneDB
    print("b4 init")
    print(database)
    await init_beanie(database=database,
                      document_models=[User, Post])


async def close_db() -> None:
    """
    Close connection to MongoDB
    :return: None
    :rtype: NoneType
    """
    setting: config.Settings = config.get_setting()
    connection_string: str = setting.mongo_connection
    client: AsyncIOMotorClient = AsyncIOMotorClient(connection_string)
    client.close()


def handle_nosql_exceptions(func: callable) -> callable:
    """
    Decorator for PyMongo Exceptions
    :param func: function to be decorated
    :return: return from func or exception raised
    """

    async def inner(*args, **kwargs) -> callable:
        try:
            return await func(*args, **kwargs)
        except ExecutionTimeout as et_err:
            print(et_err)
            # raise et_err
        except DuplicateKeyError as dk_exc:
            print(dk_exc)
            # raise dk_exc
        except InvalidName as in_exc:
            print(in_exc)
            # raise in_exc
        except InvalidOperation as io_exc:
            print(io_exc)
            # raise io_exc
        except NetworkTimeout as nt_exc:
            print(nt_exc)
            # raise nt_exc
        except NotPrimaryError as np_exc:
            print(np_exc)
            # raise np_exc
        except WriteError as w_exc:
            print(w_exc)
            # raise w_exc
        except WTimeoutError as wt_exc:
            print(wt_exc)
            # raise wt_exc
        except OperationFailure as of_exc:
            print(of_exc)
            # raise of_exc

    return inner
