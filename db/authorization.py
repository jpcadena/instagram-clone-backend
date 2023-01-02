"""
Authorization database script
"""
import aioredis
from aioredis.exceptions import DataError, AuthenticationError,\
    NoPermissionError, TimeoutError as RedisTimeoutError, \
    ConnectionError as RedisConnectionError
from core import config


async def init_auth_db() -> None:
    """
    Init connection to Redis Database
    :return: None
    :rtype: NoneType
    """
    setting: config.Settings = config.get_setting()
    url: str = setting.redis_endpoint
    await aioredis.from_url(url, decode_responses=True)


def handle_redis_exceptions(func: callable) -> callable:
    """
    Decorator for Redis Exceptions
    :param func: function to be decorated
    :return: return from func or exception raised
    """

    async def inner(*args, **kwargs) -> callable:
        try:
            return await func(*args, **kwargs)
            # raise et_err
        except AuthenticationError as a_exc:
            print(a_exc)
            # raise io_exc
        except RedisConnectionError as c_exc:
            print(c_exc)
            # raise dk_exc
        except DataError as d_exc:
            print(d_exc)
            # raise in_exc
        except NoPermissionError as np_exc:
            print(np_exc)
            # raise nt_exc
        except RedisTimeoutError as t_exc:
            print(t_exc)
            # raise wt_exc
    return inner
