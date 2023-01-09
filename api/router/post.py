"""
PostCreate router module for API endpoints.
"""
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, status, Path, Body
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from api.deps import get_current_user
from schemas.post import PostDisplay, PostCreate
from schemas.user import UserAuth
from services.post import PostService

router: APIRouter = APIRouter(prefix='/posts', tags=['posts'])


@router.post('', response_model=PostDisplay,
             status_code=status.HTTP_201_CREATED)
async def create_post(
        post: PostCreate = Body(
            ..., title='New post', description='New post to create'),
        current_user: UserAuth = Depends(get_current_user)) -> PostDisplay:
    """
    Create a new post into the system.
    - :param post: Body Object with image_url and caption to be created
    - :type post: PostCreate
    - :return: Post created with id, image_url, caption,
    timestamp for creation, user ID
    - :rtype: PostDisplay
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    auth_user_id: PydanticObjectId = current_user.id
    created_post: PostDisplay = await PostService.create_post(
        post, auth_user_id)
    return created_post


@router.get('/{post_id}', response_model=PostDisplay)
async def get_post(post_id: PydanticObjectId = Path(
    ..., title='PostCreate ID', description='ID of the PostCreate to searched',
    example=1), current_user: UserAuth = Depends(get_current_user)
) -> PostDisplay:
    """
    Search for specific Post by ID from the system.
    - :param post_id: Path Parameter of Post ID to search
    - :type post_id: PydanticObjectId
    - :return: Found Post from logged-in user
    - :rtype: PostDisplay
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    found_post: PostCreate = await PostService.read_post_by_id(post_id)
    if not found_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'PostCreate with ID {post_id} '
                                   f'not found in the system.')
    displayed_post: PostDisplay = PostDisplay(**found_post.dict())
    return displayed_post


@router.get('', response_model=list[PostDisplay])
async def get_posts(current_user: UserAuth = Depends(get_current_user)
                    ) -> list[PostDisplay]:
    """
    Retrieve all posts from the system.
    - :return: All posts from logged-in user
    - :rtype: list[PostDisplay]
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    posts: list[PostDisplay] = await PostService.read_all_posts()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='This user has no posts in the system.')
    return posts


@router.delete('/{post_id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: PydanticObjectId = Path(
            ..., title='Post ID', description='ID of the Post to deleted',
            example='63aefa38afda3a176c1e3562'),
        current_user: UserAuth = Depends(get_current_user)) -> Response:
    """
    Delete post by its ID from the system.
    - :param post_id: Path parameter of Post ID to be deleted.
    - :type post_id: PydanticObjectId
    - :return: Response with data about deleted Post
    - :rtype: Response
    \f
    :param current_user: Dependency method for authorization by current user
    :type current_user: UserAuth
    """
    data: dict = await PostService.delete_post(post_id)
    response: Response = Response(
        status_code=status.HTTP_204_NO_CONTENT,
        media_type='application/json')
    response.headers['deleted'] = str(data['ok']).lower()
    response.headers['deleted_at'] = str(data['deleted_at'])
    return response
