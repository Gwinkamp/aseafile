from .error import Error
from typing import List, TypeVar, Generic
from pydantic.generics import GenericModel
from http import HTTPStatus

# Type of method execution result
ContentT = TypeVar('ContentT')


class SeaResult(GenericModel, Generic[ContentT]):
    """Model for providing information about the result of executing an APi method"""

    # Indicates the success of the method execution
    success: bool

    # Http status
    status: HTTPStatus

    # List of errors
    errors: List[Error] | None

    # Result of method execution
    content: ContentT | None

    class Config:
        arbitrary_types_allowed = True
