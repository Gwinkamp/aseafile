from .base import StrEnum


class HttpMethod(StrEnum):
    """Enumeration of popular http methods"""
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    HEAD = 'head'
    PATCH = 'patch'
