"""
Main script for FastAPI app
"""
import json
from typing import Optional
from anyio.streams.file import FileReadStream, FileWriteStream
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from pydantic import AnyUrl
from api.router import user, authentication, post
from core import config
from db.authorization import init_auth_db
from db.db import init_db, close_db
from helper.helper import update_json
from schemas.msg import Msg

DESCRIPTION: str = """**FastAPI** and **Beanie** *(MongoDB)* helps you do
 awesome stuff. 🚀\n\n ![Instagram](https://camo.githubusercontent.com/4ba91c3b883e4636545386ffd115e1f8538becce7d4bc39d9b391505ac10fa0c/68747470733a2f2f7777772e70726f666573696f6e616c7265766965772e636f6d2f77702d636f6e74656e742f75706c6f6164732f323031382f30342f496e7374616772616d2d74616d62692543332541396e2d6162616e646f6e612d6c612d706c617461666f726d612d57696e646f77732d31302d4d6f62696c652e6a7067)"""
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users, such as register, get, update "
                       "and delete.",
    },
    {
        "name": "posts",
        "description": "Manage post with create, get a specific post, all "
                       "posts and delete.",
    },
    {
        "name": "authentication",
        "description": "The **login** logic is here as well as password "
                       "recovery and reset",
    },
]


def custom_generate_unique_id(route: APIRoute) -> Optional[str]:
    """
    Generate a custom unique ID for each route in API
    :param route: endpoint route
    :type route: APIRoute
    :return: new ID based on tag and route name
    :rtype: string or None
    """
    if route.name == 'root':
        return None
    return f"{route.tags[0]}-{route.name}"


settings: config.Settings = config.get_setting()


app: FastAPI = FastAPI(
    title='Instagram Clone Backend',
    description=DESCRIPTION,
    openapi_url=settings.API_V1_STR + settings.OPENAPI_FILE_PATH,
    contact={
        "name": "Juan Pablo Cadena Aguilar",
        "url": "https://www.github.com/jpcadena",
        "email": "jpcadena@espol.edu.ec"},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"},
    generate_unique_id_function=custom_generate_unique_id)
app.include_router(user.router, prefix=settings.API_V1_STR)
app.include_router(post.router, prefix=settings.API_V1_STR)
app.include_router(authentication.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> Msg:
    """
    Function to retrieve homepage.
    - :return: Welcome message
    - :rtype: Msg
    """
    return Msg('hello world!')


@app.on_event('startup')
async def startup_event():
    """
    Startup for Backend
    :return: None
    :rtype: NoneType
    """
    setting: config.Settings = config.get_setting()
    async with await FileWriteStream.from_path(
            setting.OPENAPI_FILE_PATH) as stream:
        await stream.send(json.dumps(app.openapi()).encode(
            encoding=setting.ENCODING))
    async with await FileReadStream.from_path(
            setting.OPENAPI_FILE_PATH) as stream:
        async for chunk in stream:
            print(chunk.decode(), end='')
    await update_json()
    await init_db()
    print("\nMongoDB client started")
    await init_auth_db()
    print("Redis client started")


@app.on_event('shutdown')
async def shutdown_event():
    """
    Shutdown for Backend
    :return: None
    """
    # app.mongodb_client.close()
    print("\nMongoDB client shutdown")
    await close_db()


base_url: AnyUrl = config.get_setting().SERVER_HOST.replace(':8000', '')
origins: list[AnyUrl] = [base_url + ':3000', base_url + ':3001',
                         base_url + ':3002', base_url + ':5000']
app.add_middleware(
    CORSMiddleware, allow_origins=origins,
    allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.mount('/static/images', StaticFiles(directory='static/images'),
          name='images')
