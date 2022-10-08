import aiohttp
from http import HTTPStatus
from pydantic import parse_raw_as
from typing import Type, TypeVar, Dict, Any
from .base_http_handler import BaseHttpHandler
from ..enums import HttpMethod
from ..models import SeaResult

T = TypeVar('T')


class HttpRequestHandler(BaseHttpHandler):

    def __init__(
            self,
            method: HttpMethod,
            url: str,
            token: str | None = None,
            headers: Dict[str, str] | None = None,
            query_params: Dict[str, str | int] | None = None,
            data: Any | None = None):
        super().__init__(method, url, token, headers, query_params, data)

    async def execute(self, content_type: Type[T] | None = None) -> SeaResult[T]:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                    method=self._method,
                    url=self._route,
                    headers=self._headers,
                    params=self._query_params,
                    data=self._data
            ) as response:
                response_content = await response.content.read()
                http_status = HTTPStatus(response.status)

                result = SeaResult[T](
                    success=(http_status in self.SUCCESS_STATUSES),
                    status=http_status,
                    errors=None,
                    content=None
                )

                if result.success:
                    if content_type is not None:
                        result.content = parse_raw_as(content_type, response_content)
                else:
                    result.errors = self._try_parse_errors(response_content)

                return result
