import aiohttp
from typing import Dict, List, BinaryIO, Any
from urllib.parse import urljoin
from .enums import *
from .models import *
from .builders import QueryParams
from .route_storage import RouteStorage
from .http_handlers import HttpRequestHandler, HttpDownloadHandler


class SeafileHttpClient:
    """Httpclient providing seafile web api methods."""

    def __init__(self, base_url: str):
        self._version = 'v2.1'
        self._token = None
        self._base_url = base_url
        self._route_storage = RouteStorage()

    @property
    def version(self):
        """Web api version (currently supported only v2.1)"""
        return self._version

    @property
    def base_url(self):
        """Seafile base url"""
        return self._base_url

    @property
    def token(self) -> str | None:
        """Access token"""
        return self._token

    async def ping(self):
        """Ping seafile service

        :return: SeaResult object with "pong" response
        """
        method_url = urljoin(self.base_url, self._route_storage.ping)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url
        )
        return await handler.execute(content_type=str)

    async def auth_ping(self, token: str | None = None):
        """Ping seafile service with access token.

        :param token: access token
        :return: SeaResult object with "pong" response
        """
        method_url = urljoin(self.base_url, self._route_storage.auth_ping)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token
        )

        return await handler.execute(content_type=str)

    async def obtain_auth_token(self, username: str, password: str):
        """Obtain access token

        :param username: seafile login
        :param password: seafile password
        :returns: SeaResult object with access token
        """
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
        """Authorize in seafile and save access token in context

        :param username: seafile login
        :param password: seafile password
        """
        result = await self.obtain_auth_token(username, password)

        if not result.success:
            raise Exception(
                'Error when obtain the token: ' + ', '.join(
                    e.message for e in result.errors or [Error(title='unknown', message='unknown error')]))

        self._token = result.content.token

    async def get_default_repo(self, token: str | None = None):
        """Get repository id for default repository

        :param token: access token
        :returns: SeaResult object with repository id
        """
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
        """Create default repository if it doesn't exist

        :param token: access token
        :returns: SeaResult object with repository id
        """
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
        """Get list of repos

        :param repo_t: repository types to be returned (mine, shared, group, org)
        :param token: access token
        :returns: SeaResult object with list of RepoItem
        """
        method_url = urljoin(self.base_url, self._route_storage.repos)

        query_params = QueryParams()
        query_params.add_param_if_exists('type', repo_t)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[RepoItem])

    async def create_repo(self, repo_name: str, token: str | None = None) -> SeaResult[RepoItem]:
        """Create repo

        :param repo_name: name of repository being created
        :param token: access token
        :returns: SeaResult object with RepoItem that will be created
        """
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
                type=ItemType.REPOSITORY,
                name=response.content['repo_name'],
                mtime=response.content['mtime'],
                permission=response.content['permission'],
                size=response.content['repo_size'],
                owner=response.content['email']
            )

        return result

    async def delete_repo(self, repo_id: str, token: str | None = None):
        """Delete repo

        :param repo_id: id of repository to be deleted
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.repo(repo_id))

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token
        )

        return await handler.execute()

    async def get_upload_link(self, repo_id: str, dir_path: str, token: str | None = None):
        """Get a link to upload file

        :param repo_id: id of repository where file will be uploaded
        :param dir_path: path to the directory where file should be uploaded
        :param token: access token
        :returns: SeaResult object with upload link
        """
        method_url = urljoin(self.base_url, self._route_storage.get_upload_link(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', dir_path)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
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
        """Upload file

        :param repo_id: id of repository where file will be uploaded
        :param dir_path: path to directory where file will be uploaded
        :param filename: name of uploaded file
        :param payload: file contents
        :param replace: indicates whether file should be overwritten if it already exists
        :param relative_path: sub-folder of "parent_dir", if this sub-folder does not exist, Seafile will create it recursively
        :param token: access token
        :returns: SeaResult object with UploadedFileItem
        """
        upload_ilnk_response = await self.get_upload_link(repo_id, dir_path, token)

        if not upload_ilnk_response.success:
            return SeaResult[UploadedFileItem](
                success=upload_ilnk_response.success,
                status=upload_ilnk_response.status,
                errors=upload_ilnk_response.errors,
                content=None
            )

        query_params = QueryParams()
        query_params.add_param('ret-json', 1)

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
            query_params=query_params.get_result(),
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
        """Upload multiple files

        :param repo_id: id of repository where files will be uploaded
        :param dir_path: path to directory where files will be uploaded
        :param files: list of named tuples from file name and its contents
        :param replace: indicates whether the file should be overwritten if it already exists
        :param relative_path: sub-folder of "parent_dir", if this sub-folder does not exist, Seafile will create it recursively
        :param token: access token
        :returns: SeaResult object with list of UploadedFileItem
        """
        upload_ilnk_response = await self.get_upload_link(repo_id, dir_path, token)

        if not upload_ilnk_response.success:
            SeaResult[List[UploadedFileItem]](
                success=upload_ilnk_response.success,
                status=upload_ilnk_response.status,
                errors=upload_ilnk_response.errors,
                content=[]
            )

        query_params = QueryParams()
        query_params.add_param('ret-json', 1)

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
            query_params=query_params.get_result(),
            data=data
        )

        return await handler.execute(content_type=List[UploadedFileItem])

    async def get_download_link(self, repo_id: str, filepath: str, reuse: bool = False, token: str | None = None):
        """Get a link to download file

        :param repo_id: id of repository to download file from
        :param filepath: path to file to download
        :param reuse: indicates of reuse. set it to True if you want the generated download link to be accessed more than once within one hour.
        :param token: access token
        :returns: SeaResult object with link to download file
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)
        query_params.add_param('reuse', int(reuse))

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=str)

    async def download(self, repo_id, filepath: str, token: str | None = None):
        """Download file

        :param repo_id: id of repository to download file from
        :param filepath: path to file to download
        :param token: access token
        """
        response = await self.get_download_link(repo_id, filepath, token=token)

        if not response.success:
            return SeaResult[bytes](
                success=response.success,
                status=response.status,
                errors=response.errors,
                content=None
            )

        handler = HttpDownloadHandler(
            method=HttpMethod.GET,
            url=response.content,
            token=token or self.token
        )

        return await handler.execute()

    async def get_file_detail(self, repo_id: str, filepath: str, token: str | None = None):
        """Get detail information about the file

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param token: access token
        :returns: SeaResult object with FileItemDetail
        """
        method_url = urljoin(self.base_url, self._route_storage.file_detail(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=FileItemDetail)

    async def create_file(self, repo_id: str, filepath: str, token: str | None = None):
        """Create new file

        :param repo_id: id of repository to create file in
        :param filepath: path to new file
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.CREATE)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
            data=data
        )

        return await handler.execute()

    async def rename_file(self, repo_id: str, filepath: str, new_filename: str, token: str | None = None):
        """Rename file

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param new_filename: new name of file
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.RENAME)
        data.add_field('newname', new_filename)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
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
        """Move file to another location

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param dst_dir: directory where file will be moved
        :param dst_repo_id: id of repository where file will be moved
        :param token: access token
        :returns: SeaResult object with a link to new file location
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.MOVE)
        data.add_field('dst_dir', dst_dir)
        data.add_field('dst_repo', dst_repo_id or repo_id)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
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
        """Copy file

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param dst_dir: directory where a copy of file will be created
        :param dst_repo_id: id of repository where a copy of file will be created
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.COPY)
        data.add_field('dst_dir', dst_dir)
        data.add_field('dst_repo', dst_repo_id or repo_id)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
            data=data
        )

        return await handler.execute()

    async def delete_file(self, repo_id: str, filepath: str, token: str | None = None):
        """Delete file

        :param repo_id: id of repository where file is located
        :param filepath: path to file to be deleted
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.file(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', filepath)

        data = aiohttp.FormData()
        data.add_field('operation', FileOperation.DELETE)

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result(),
            data=data
        )

        return await handler.execute()

    async def lock_file(self, repo_id: str, filepath: str, token: str | None = None):
        """Lock file

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param token: access token
        """
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
        """Unlock file

        :param repo_id: id of repository where file is located
        :param filepath: path to file
        :param token: access token
        """
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
        """Get all items in a directory

        :param repo_id: id of repository to get information from
        :param path: path to directory where you need to find out what is located
        :param token: access token
        :returns: SeaResult object with list of BaseItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path or '/')

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[BaseItem])

    async def get_items_by_id(self, repo_id: str, dir_id: str, token: str | None = None):
        """Get all items in a directory by directory id

        :param repo_id: id of repository to get information from
        :param dir_id: id of directory where you need to find out what is located
        :param token: access token
        :returns: SeaResult object with list of BaseItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('oid', dir_id)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[BaseItem])

    async def get_files(self, repo_id: str, path: str | None = None, token: str | None = None):
        """Get all files in a directory

        :param repo_id: id of repository to get information from
        :param path: path to directory where you need to find out what is located
        :param token: access token
        :returns: SeaResult object with list of FileItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path or '/')
        query_params.add_param('t', 'f')

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[FileItem])

    async def get_files_by_id(self, repo_id: str, dir_id: str, token: str | None = None):
        """Get all files in a directory by directory id

        :param repo_id: id of repository to get information from
        :param dir_id: id of directory where you need to find out what is located
        :param token: access token
        :returns: SeaResult object with list of FileItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('oid', dir_id)
        query_params.add_param('t', 'f')

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[FileItem])

    async def get_directories(
            self,
            repo_id: str,
            path: str | None = None,
            recursive: bool = False,
            token: str | None = None):
        """Get all directories in a directory

        :param repo_id: id of repository to get information from
        :param path: path to directory where you need to find out what is located
        :param recursive: indicates a recursive search method
        :param token: access token
        :returns: SeaResult object with list of DirectoryItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path or '/')
        query_params.add_param('t', 'd')
        query_params.add_param('recursive', int(recursive))

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[DirectoryItem])

    async def get_directories_by_id(
            self,
            repo_id: str,
            dir_id: str,
            recursive: bool = False,
            token: str | None = None):
        """Get all directories in a directory by directory id

        :param repo_id: id of repository to get information from
        :param dir_id: id of directory where you need to find out what is located
        :param recursive: indicates a recursive search method
        :param token: access token
        :returns: SeaResult object with list of DirectoryItem
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('oid', dir_id)
        query_params.add_param('t', 'd')
        query_params.add_param('recursive', int(recursive))

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=List[DirectoryItem])

    async def get_directory_detail(self, repo_id: str, path: str, token: str | None = None):
        """Get detailed information about the directory

        :param repo_id: id of repository where directory is located
        :param path: path to directory
        :param token: access token
        :returns: SeaResult object with DirectoryItemDetail
        """
        if path == '/':
            raise ValueError('Path should not be "/"')

        method_url = urljoin(self.base_url, self._route_storage.dir_detail(repo_id))

        query_params = QueryParams()
        query_params.add_param('path', path)

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=DirectoryItemDetail)

    async def create_directory(self, repo_id: str, path: str, token: str | None = None):
        """Create new directory

        :param repo_id: id of repository where directory will be created
        :param path: path to directory
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path)

        data = aiohttp.FormData()
        data.add_field('operation', DirectoryOperation.CREATE)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            data=data,
            query_params=query_params.get_result()
        )

        return await handler.execute()

    async def rename_directory(self, repo_id: str, path: str, new_name: str, token: str | None = None):
        """Rename directory

        :param repo_id: id of repository where directory is located
        :param path: path to directory
        :param new_name: new name of directory
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path)

        data = aiohttp.FormData()
        data.add_field('operation', DirectoryOperation.RENAME)
        data.add_field('newname', new_name)

        handler = HttpRequestHandler(
            method=HttpMethod.POST,
            url=method_url,
            token=token or self.token,
            data=data,
            query_params=query_params.get_result()
        )

        return await handler.execute()

    async def delete_directory(self, repo_id: str, path: str, token: str | None = None):
        """Delete directory

        :param repo_id: id of repository where directory will be deleted
        :param path: path to directory
        :param token: access token
        """
        method_url = urljoin(self.base_url, self._route_storage.dir(repo_id))

        query_params = QueryParams()
        query_params.add_param('p', path)

        handler = HttpRequestHandler(
            method=HttpMethod.DELETE,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute()

    async def get_smart_link(self, repo_id: str, path: str, is_dir: bool = False, token: str | None = None):
        """Get smart link to item

        :param repo_id: id of repository where item is located
        :param path: path to item
        :param is_dir: indicates that the item is a directory
        :param token: access token
        :returns: SeaResult with smart-link
        """
        method_url = urljoin(self.base_url, self._route_storage.smart_link)

        query_params = QueryParams()
        query_params.add_param('repo_id', repo_id)
        query_params.add_param('path', path)
        query_params.add_param('is_dir', str(is_dir).lower())

        handler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        return await handler.execute(content_type=SmartLink)

    async def search_file(
            self,
            query: str,
            repo_id: str,
            token: str | None = None
    ):
        """Search files in repositories

        :param query: keyword for searching
        :param repo_id: id of repository where search will be performed
        :param token: access token
        :returns: SeaResult with list of SearchResultItem
        """
        method_url = urljoin(self.base_url, self._route_storage.search_file)

        query_params = QueryParams()
        query_params.add_param('q', query)
        query_params.add_param('repo_id', repo_id)

        hanndler = HttpRequestHandler(
            method=HttpMethod.GET,
            url=method_url,
            token=token or self.token,
            query_params=query_params.get_result()
        )

        response = await hanndler.execute(content_type=SearchResult)
        result = SeaResult[List[SearchResultItem]](
            success=response.success,
            status=response.status,
            errors=response.errors,
            content=None
        )

        if result.success and response.content is not None:
            result.content = response.content.data

        return result
