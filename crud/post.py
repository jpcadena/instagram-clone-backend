"""
CRUD Post script
"""
from crud import Filter, Specification
from models.post import Post


class PostFilter(Filter):
    """
    Post Filter class based on Filter for ID.
    """

    async def filter(self, spec: Specification):
        post: Post = await Post.get(spec.value)
        return post


class PostsFilter(Filter):
    """
    Posts Filter class based on Filter.
    """

    async def filter(self, spec: Specification = None):
        posts: list[Post] = await Post.find_all().to_list()
        return posts
