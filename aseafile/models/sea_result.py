from typing import Dict, List, TypeVar, Generic
from pydantic.generics import GenericModel
from http import HTTPStatus


ContentT = TypeVar('ContentT')


class SeaResult(GenericModel, Generic[ContentT]):
    success: bool
    status: HTTPStatus
    errors: Dict[str, List[str]] | None
    content: ContentT | None
