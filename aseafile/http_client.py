import aiohttp
from http import HTTPStatus
from typing import Dict, List
from pydantic import parse_raw_as
from urllib.parse import urljoin
from pydantic import HttpUrl
from aseafile.seafile import RouteStorage
from aseafile.models import SeaResult


class SeafileHttpClient:

    def __init__(self, base_url: HttpUrl):
        self._version = 'v2.1'
        self._token = None
        self._base_url = base_url
        self._route_storage = RouteStorage()

    @property
    def version(self):
        return self._version

    @property
    def base_url(self):
        return self._base_url

    @property
    def token(self):
        return self._token

    async def ping(self):
        method_url = urljoin(self.base_url, self._route_storage.ping)

        async with aiohttp.ClientSession() as session:
            async with session.get(url=method_url) as response:
                response_content = await response.text()
                http_status = HTTPStatus(response.status)

                result = SeaResult[str](
                    success=(http_status == HTTPStatus.OK),
                    status_code=http_status,
                    errors=None,
                    content=response_content
                )

                if result.status_code == HTTPStatus.BAD_REQUEST:
                    result.errors = self.try_parse_errors(response_content)

                return result

    async def auth_ping(self, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.auth_ping)

        headers = {'Authorization': f'Token {token or self.token}'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=method_url, headers=headers) as response:
                response_content = await response.text()
                http_status = HTTPStatus(response.status)

                result = SeaResult[str](
                    success=(http_status == HTTPStatus.OK),
                    status_code=http_status,
                    errors=None,
                    content=response_content
                )

                if result.status_code == HTTPStatus.BAD_REQUEST:
                    result.errors = self.try_parse_errors(response_content)

                return result

    async def obtain_auth_token(self, username: str, password: str):
        method_url = urljoin(self.base_url, self._route_storage.auth_token)

        data = aiohttp.FormData()
        data.add_field('username', username)
        data.add_field('password', password)

        async with aiohttp.ClientSession() as session:
            async with session.post(url=method_url, data=data) as response:
                http_status = HTTPStatus(response.status)

                token = ...
                errors = ...
                response_content = ...

                if http_status == HTTPStatus.OK:
                    response_content = await response.json()
                    token = response_content.get('token')
                    errors = None
                elif http_status == HTTPStatus.BAD_REQUEST:
                    response_content = await response.text()
                    token = None
                    errors = self.try_parse_errors(response_content)
                else:
                    pass  # TODO: предусмотреть другие кейсы

                return SeaResult[str](
                    success=(http_status == HTTPStatus.OK),
                    status_code=http_status,
                    errors=errors,
                    content=token
                )

    async def authorize(self, username: str, password: str):
        response = await self.obtain_auth_token(username, password)

        if not response.success:
            # TODO: добавить логирование
            raise Exception(f'fail')

        self._token = response.token

    def try_parse_errors(self, response_content: str):
        try:
            return parse_raw_as(Dict[str, List[str]], response_content)
        except Exception as e:
            # TODO: добавить логирование
            print(e)
