import aiohttp
from http import HTTPStatus
from pydantic import parse_raw_as
from typing import Type, TypeVar, Dict, List, Any
from aseafile.enums import HttpMethod
from aseafile.exceptions import UnauthorizedError
from aseafile.models import SeaResult, Error

T = TypeVar('T')


class HttpRequestHandler:
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
        self._headers = dict()
        if token is not None:
            self._headers |= self._create_authorization_headers(token)
        if headers is not None:
            self._headers |= headers

    async def execute(self, content_type: Type[T] | None = None) -> SeaResult[T]:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=self._method,
                    url=self._route,
                    headers=self._headers,
                    params=self._query_params,
                    data=self._data
            ) as response:
                response_content = await response.read()
                http_status = HTTPStatus(response.status)

                result = SeaResult[T](
                    success=(http_status in self.SUCCESS_STATUSES),
                    status=http_status,
                    errors=None,
                    content=None
                )

                if result.success:
                    if content_type is not None:
                        if content_type is bytes:
                            result.content = response_content
                        else:
                            result.content = parse_raw_as(content_type, response_content)
                else:
                    result.errors = self._try_parse_errors(response_content)

                return result

    @classmethod
    def _try_parse_errors(cls, response_content: str | bytes):
        try:
            errors = parse_raw_as(Dict[str, Any], response_content)
            result = list()
            for key, value in errors.items():
                if isinstance(value, list):
                    result.append(Error(title=key, message='; '.join(value)))
                elif isinstance(value, str):
                    result.append(Error(title=key, message=value))
                else:
                    pass  # TODO: добавить логирование

            return result
        except Exception:
            pass  # TODO: добавить логирование

    @staticmethod
    def _create_authorization_headers(token: str | None):
        if token is None:
            # TODO: добавить логирование
            raise UnauthorizedError()

        return {'Authorization': f'Token {token}'}
