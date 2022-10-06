from .base import StrEnum


class HttpMethod(StrEnum):
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'
    HEAD = 'head'
    PATCH = 'patch'
