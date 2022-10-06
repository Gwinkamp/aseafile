import pytest
import aiofiles
from typing import List
from http import HTTPStatus
from pathlib import PurePath
from assertpy import assert_that
from aseafile_tests.config import BASE_DIR
from aseafile.models import FileItemDetail, SmartLink, UploadedFileItem
from aseafile_tests.test_data.context import TestContext


@pytest.mark.incremental
@pytest.mark.usefixtures("use_test_directory")
@pytest.mark.usefixtures("use_custom_assertions")
class TestFilesManagement:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('filename', 'test.md')
        self.context.add('dirpath', '/')

    @pytest.mark.asyncio
    async def test_create_file(self, test_repo, authorized_http_client):
        # Arrange
        filename = self.context.get('filename')
        dirpath = self.context.get('dirpath')

        # Act
        result = await authorized_http_client.create_file(test_repo, dirpath + filename)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.CREATED)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()

    @pytest.mark.asyncio
    async def test_get_file_detail(self, test_repo, authorized_http_client):
        # Arrange
        filename = self.context.get('filename')
        dirpath = self.context.get('dirpath')

        # Act
        result = await authorized_http_client.get_file_detail(test_repo, dirpath + filename)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(FileItemDetail)

    @pytest.mark.asyncio
    async def test_rename_file(self, test_repo, authorized_http_client):
        # Arrange
        filename = self.context.get('filename')
        dirpath = self.context.get('dirpath')
        new_filename = 'test2.md'

        # Act
        result = await authorized_http_client.rename_file(test_repo, dirpath + filename, new_filename)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()

        # Save context
        self.context.add('filename', new_filename)

    @pytest.mark.asyncio
    async def test_move_file(self, test_repo, authorized_http_client):
        # Arrange
        filename = self.context.get('filename')
        dirpath = self.context.get('dirpath')
        new_dirpath = '/test_dir/'

        # Act
        result = await authorized_http_client.move_file(test_repo, dirpath + filename, dst_dir=new_dirpath)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none().is_not_empty()

        # Save context
        self.context.add('dirpath', new_dirpath)

    @pytest.mark.asyncio
    async def test_copy_file(self, test_repo, authorized_http_client):
        # Arrange
        filename = self.context.get('filename')
        dirpath = self.context.get('dirpath')

        # Act
        dst_dir = '/'
        result = await authorized_http_client.copy_file(test_repo, dirpath + filename, dst_dir=dst_dir)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()

        # Save context
        self.context.add('copy', dst_dir + filename)

    @pytest.mark.asyncio
    async def test_get_upload_link(self, test_repo, authorized_http_client):
        # Arrange
        dirpath = self.context.get('dirpath')

        # Act
        result = await authorized_http_client.get_upload_link(test_repo, dirpath)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none()

    @pytest.mark.asyncio
    async def test_get_download_link(self, test_repo, authorized_http_client):
        # Arrange
        filepath = self.context.get('copy')

        # Act
        result = await authorized_http_client.get_download_link(test_repo, filepath, reuse=True)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none().is_not_empty()

    @pytest.mark.asyncio
    async def test_get_smart_link(self, test_repo, authorized_http_client):
        # Arrange
        filepath = self.context.get('copy')

        # Act
        result = await authorized_http_client.get_smart_link(test_repo, filepath)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(SmartLink)

    @pytest.mark.asyncio
    async def test_delete_file(self, test_repo, authorized_http_client):
        # Arrange
        filepath = self.context.get('copy')

        # Act
        result = await authorized_http_client.delete_file(test_repo, filepath)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()


@pytest.mark.incremental
@pytest.mark.usefixtures("use_custom_assertions")
class TestUploadAndDownloadFiles:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('dirpath', '/')
        self.context.add('file_0', 'uploaded.md')
        self.context.add('file_1', 'test_file_1.txt')
        self.context.add('file_2', 'test_file_2.txt')
        self.context.add('file_3', 'test_file_3.txt')
        self.context.add('local_test_files_dir', BASE_DIR / 'test_data' / 'files')

    @pytest.mark.asyncio
    async def test_upload_file(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.get('dirpath')
        filename = self.context.get('file_0')
        local_test_files_dir = self.context.typed_get('local_test_files_dir', PurePath)

        # Act
        async with aiofiles.open(local_test_files_dir / filename, 'rb') as file:
            result = await authorized_http_client.upload(test_repo, dir_path, filename, file)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(UploadedFileItem)

    @pytest.mark.asyncio
    async def test_download_file(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.get('dirpath')
        filename = self.context.get('file_0')
        local_test_files_dir = self.context.typed_get('local_test_files_dir', PurePath)

        # Act
        result = await authorized_http_client.download(test_repo, dir_path + filename)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(bytes)

        async with aiofiles.open(local_test_files_dir / filename, 'rb') as file:
            expected_content = await file.read()
            assert_that(result.content).is_equal_to(expected_content)

    @pytest.mark.asyncio
    async def test_multiple_upload_files(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.get('dirpath')
        filename_1 = self.context.get('file_1')
        filename_2 = self.context.get('file_2')
        filename_3 = self.context.get('file_3')
        local_test_files_dir = self.context.typed_get('local_test_files_dir', PurePath)

        async with aiofiles.open(local_test_files_dir / filename_1, 'rb') as file_1:
            payload_1 = await file_1.read()

        async with aiofiles.open(local_test_files_dir / filename_2, 'rb') as file_1:
            payload_2 = await file_1.read()

        async with aiofiles.open(local_test_files_dir / filename_3, 'rb') as file_1:
            payload_3 = await file_1.read()

        files = [
            {'filename': filename_1, 'payload': payload_1},
            {'filename': filename_2, 'payload': payload_2},
            {'filename': filename_3, 'payload': payload_3}
        ]

        # Act
        result = await authorized_http_client.uploads(test_repo, dir_path, files)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(List)
        assert_that(result.content).contains_item(lambda item: item.name == filename_1)
        assert_that(result.content).contains_item(lambda item: item.name == filename_2)
        assert_that(result.content).contains_item(lambda item: item.name == filename_3)
