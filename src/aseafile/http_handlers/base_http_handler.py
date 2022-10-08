from http import HTTPStatus
from typing import Dict, Any
from pydantic import parse_raw_as
from ..enums import HttpMethod
from abc import ABCMeta, abstractmethod
from ..exceptions import UnauthorizedError
from ..models import SeaResult, Error


class BaseHttpHandler(metaclass=ABCMeta):
    SUCCESS_STATUSES = (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NON_AUTHORITATIVE_INFORMATION,
        HTTPStatus.NO_CONTENT,
        HTTPStatus.RESET_CONTENT,
        HTTPStatus.PARTIAL_CONTENT,
        HTTPStatus.MULTI_STATUS,
        HTTPStatus.ALREADY_REPORTED,
        HTTPStatus.IM_USED
    )

    def __init__(
            self,
            method: HttpMethod,
            url: str,
            token: str | None = None,
            headers: Dict[str, str] | None = None,
            query_params: Dict[str, str | int] | None = None,
            data: Any | None = None):
        self._method = method
        self._route = url
        self._data = data
        self._token = token
        self._query_params = query_params
        self._headers: Dict[str, str] = dict()
        if token is not None:
            self._headers |= self._create_authorization_headers(token)
        if headers is not None:
            self._headers |= headers

    @abstractmethod
    async def execute(self, *args, **kwargs) -> SeaResult:
        ...

    @staticmethod
    def _try_parse_errors(response_content: str | bytes):
        try:
            errors = parse_raw_as(Dict[str, Any], response_content)
            result = list()
            for key, value in errors.items():
                if isinstance(value, list):
                    result.append(Error(title=key, message='; '.join(value)))
                else:
                    result.append(Error(title=key, message=value))

            return result
        except Exception:
            pass

    @staticmethod
    def _create_authorization_headers(token: str | None):
        if token is None:
            raise UnauthorizedError('Undefined token')

        return {'Authorization': f'Token {token}'}
