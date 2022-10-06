import aiohttp
from typing import Dict, List, BinaryIO, Any
from urllib.parse import urljoin
from pydantic import HttpUrl
from aseafile.route_storage import RouteStorage
from aseafile.http_handlers import HttpRequestHandler, HttpDownloadHandler
from aseafile.models import *
from aseafile.enums import *


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
    def token(self) -> str | None:
        return self._token

    async def ping(self):
        method_url = urljoin(self.base_url, self._route_storage.ping)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url
        )
        return await handler.execute(content_type=str)

    async def auth_ping(self, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.auth_ping)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token
        )

        return await handler.execute(content_type=str)

    async def obtain_auth_token(self, username: str, password: str):
        method_url = urljoin(self.base_url, self._route_storage.auth_token)

        data = aiohttp.FormData()
        data.add_field('username', username)
        data.add_field('password', password)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            data=data
        )

        return await handler.execute(content_type=TokenContainer)

    async def authorize(self, username: str, password: str):
        result = await self.obtain_auth_token(username, password)

        if not result.success:
            raise Exception('Error when obtain the token: ' + ', '.join(e.message for e in result.errors))

        self._token = result.content.token

    async def get_default_repo(self, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.default_repo)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token
        )

        response = await handler.execute(content_type=Dict[str, Any])
        result = SeaResult[str](
            success=response.success,
            status=response.status,
            errors=response.errors,
            content=None
        )

        if not result.success:
            return result

        if response.content:
            result.content = response.content['repo_id']
        return result

    async def create_default_repo(self, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.default_repo)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token
        )

        response = await handler.execute(content_type=Dict[str, Any])
        result = SeaResult[str](
            success=response.success,
            status=response.status,
            errors=response.errors,
            content=None
        )

        if not result.success:
            return result

        if response.content:
            result.content = response.content['repo_id']

        return result

    async def get_repos(self, repo_t: RepoType | None = None, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.repos)
        query_params: Dict[str, str | int] | None = None

        if repo_t is not None:
            query_params = {'type': repo_t}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[RepoItem])

    async def create_repo(self, repo_name: str, token: str | None = None) -> SeaResult[RepoItem]:
        method_url = urljoin(self.base_url, self._route_storage.repos)

        data = aiohttp.FormData()
        data.add_field('name', repo_name)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            data=data
        )

        response = await handler.execute(content_type=Dict[str, Any])
        result = SeaResult[RepoItem](
            success=response.success,
            status=response.status,
            errors=response.errors,
            content=None
        )

        if not result.success:
            return result

        if response.content:
            result.content = RepoItem(
                id=response.content['repo_id'],
                type=ItemType.REPO,
                name=response.content['repo_name'],
                mtime=response.content['mtime'],
                permission=response.content['permission'],
                size=response.content['repo_size'],
                owner=response.content['email']
            )

        return result

    async def delete_repo(self, repo_id: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.repo(repo_id))

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token
        )

        return await handler.execute()

    async def get_upload_link(self, repo_id: str, dir_path: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.get_upload_link(repo_id))
        query_params: Dict[str, str | int] = {'p': dir_path}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=str)

    async def upload(
            self,
            repo_id: str,
            dir_path: str,
            filename: str,
            payload: BinaryIO,
            replace: bool = False,
            relative_path: str | None = None,
            token: str | None = None
    ):
        upload_ilnk_response = await self.get_upload_link(repo_id, dir_path)

        if not upload_ilnk_response.success:
            SeaResult[UploadedFileItem](
                success=upload_ilnk_response.success,
                status=upload_ilnk_response.status,
                errors=upload_ilnk_response.errors,
                content=None
            )

        query_params: Dict[str, str | int] = {'ret-json': 1}

        data = aiohttp.FormData()
        data.add_field('file', payload, filename=filename)
        data.add_field('parent_dir', dir_path)
        data.add_field('replace', str(int(replace)))

        if relative_path is not None:
            data.add_field('relative_path', relative_path)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=upload_ilnk_response.content,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        upload_response = await handler.execute(content_type=List[UploadedFileItem])
        result = SeaResult[UploadedFileItem](
            success=upload_response.success,
            status=upload_response.status,
            errors=upload_response.errors,
            content=None
        )

        if result.success and upload_response.content is not None:
            result.content = upload_response.content.pop()

        return result

    async def uploads(
            self,
            repo_id: str,
            dir_path: str,
            files: List[UploadFile],
            replace: bool = False,
            relative_path: str | None = None,
            token: str | None = None):
        upload_ilnk_response = await self.get_upload_link(repo_id, dir_path)

        if not upload_ilnk_response.success:
            SeaResult[List[UploadedFileItem]](
                success=upload_ilnk_response.success,
                status=upload_ilnk_response.status,
                errors=upload_ilnk_response.errors,
                content=[]
            )

        query_params: Dict[str, str | int] = {'ret-json': 1}

        data = aiohttp.FormData()
        data.add_field('parent_dir', dir_path)
        data.add_field('replace', str(int(replace)))
        for file in files:
            data.add_field('file', file['payload'], filename=file['filename'])

        if relative_path is not None:
            data.add_field('relative_path', relative_path)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=upload_ilnk_response.content,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute(content_type=List[UploadedFileItem])

    async def get_download_link(self, repo_id: str, filepath: str, reuse: bool = False, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        if reuse:
            query_params['reuse'] = 1

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=str)

    async def download(self, repo_id, filepath: str, token: str | None = None):
        response = await self.get_download_link(repo_id, filepath, token=token)

        if not response.success:
            return SeaResult[bytes](
                success=response.success,
                status=response.status,
                errors=response.errors,
                content=None
            )

        handdler = HttpDownloadHandler(
            method=HttpMethod.GET,
            url=response.content
        )

        return await handdler.execute()

    async def get_file_detail(self, repo_id: str, filepath: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file_detail(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=FileItemDetail)

    async def create_file(self, repo_id: str, filepath: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.CREATE)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute()

    async def rename_file(self, repo_id: str, filepath: str, new_filename: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.RENAME)
        data.add_field('newname', new_filename)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute()

    async def move_file(
            self,
            repo_id: str,
            filepath: str,
            dst_dir: str,
            token: str | None = None,
            dst_repo_id: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.MOVE)
        data.add_field('dst_dir', dst_dir)
        data.add_field('dst_repo', dst_repo_id or repo_id)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute(content_type=str)

    async def copy_file(
            self,
            repo_id: str,
            filepath: str,
            dst_dir: str,
            token: str | None = None,
            dst_repo_id: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.COPY)
        data.add_field('dst_dir', dst_dir)
        data.add_field('dst_repo', dst_repo_id or repo_id)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute()

    async def delete_file(self, repo_id: str, filepath: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))
        query_params: Dict[str, str | int] = {'p': filepath}

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.DELETE)

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token,
            query_params=query_params,
            data=data
        )

        return await handler.execute()

    async def lock_file(self, repo_id: str, filepath: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        data = aiohttp.FormData()
        data.add_field('p', filepath)
        data.add_field('operation', FileOperation.LOCK)

        handler = HttpRequestHandler(
            method=HttpMethod.PUT,
            url=method_url,
            token=token or self.token,
            data=data
        )

        return await handler.execute()

    async def unlock_file(self, repo_id: str, filepath: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        data = aiohttp.FormData()
        data.add_field('p', filepath)
        data.add_field('operation', FileOperation.UNLOCK)

        handler = HttpRequestHandler(
            method=HttpMethod.PUT,
            url=method_url,
            token=token or self.token,
            data=data
        )

        return await handler.execute()

    async def get_items(self, repo_id: str, path: str | None = None, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {'p': path or '/'}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[BaseItem])

    async def get_items_by_id(self, repo_id: str, dir_id: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {'oid': dir_id}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[BaseItem])

    async def get_files(self, repo_id: str, path: str | None = None, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {
            'p': path or '/',
            't': 'f'
        }

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[FileItem])

    async def get_files_by_id(self, repo_id: str, dir_id: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {
            'oid': dir_id,
            't': 'f'
        }

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[FileItem])

    async def get_directories(
            self,
            repo_id: str,
            path: str | None = None,
            recursive: bool = False,
            token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {
            'p': path or '/',
            't': 'd'
        }

        if recursive:
            query_params['recursive'] = 1

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[DirectoryItem])

    async def get_directories_by_id(
            self,
            repo_id: str,
            dir_id: str,
            recursive: bool = False,
            token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {
            'oid': dir_id,
            't': 'd'
        }

        if recursive:
            query_params['recursive'] = 1

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=List[DirectoryItem])

    async def get_directory_detail(self, repo_id: str, path: str, token: str | None = None):
        if path == '/':
            raise ValueError('Path should not be "/"')

        method_url = urljoin(self.base_url, self._route_storage.dir_detail(repo_id))
        query_params: Dict[str, str | int] = {'path': path}

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=DirectoryItemDetail)

    async def create_directory(self, repo_id: str, path: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {'p': path}

        data = aiohttp.FormData()
        data.add_field('operation', DirectoryOperation.CREATE)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            data=data,
            query_params=query_params
        )

        return await handler.execute()

    async def rename_directory(self, repo_id: str, path: str, new_name: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {'p': path}

        data = aiohttp.FormData()
        data.add_field('operation', DirectoryOperation.RENAME)
        data.add_field('newname', new_name)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            data=data,
            query_params=query_params
        )

        return await handler.execute()

    async def delete_directory(self, repo_id: str, path: str, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))
        query_params: Dict[str, str | int] = {'p': path}

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute()

    async def get_smart_link(self, repo_id: str, path: str, is_dir: bool = False, token: str | None = None):
        method_url = urljoin(self.base_url, self._route_storage.smart_link)
        query_params: Dict[str, str | int] = {
            'repo_id': repo_id,
            'path': path,
            'is_dir': str(is_dir).lower()
        }

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params
        )

        return await handler.execute(content_type=SmartLink)
