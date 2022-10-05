import pytest
from http import HTTPStatus
from assertpy import assert_that
from aseafile.models import FileItemDetail, SmartLink
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
