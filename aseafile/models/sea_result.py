from .error import Error
from typing import List, TypeVar, Generic
from pydantic.generics import GenericModel
from http import HTTPStatus

ContentT = TypeVar('ContentT')


class SeaResult(GenericModel, Generic[ContentT]):
    success: bool
    status: HTTPStatus
    errors: List[Error] | None
    content: ContentT | None
