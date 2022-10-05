import pytest
from http import HTTPStatus
from assertpy import assert_that
from aseafile.models import DirectoryItemDetail
from aseafile_tests.test_data.context import TestContext


@pytest.mark.incremental
@pytest.mark.usefixtures("use_custom_assertions")
class TestDirectoriesManagement:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('dir_path', '/')
        self.context.add('dir_name', 'test_dir')

    @pytest.mark.asyncio
    async def test_create_directory(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)

        # Act
        result = await authorized_http_client.create_directory(test_repo, dir_path + dir_name)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.CREATED)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()

    @pytest.mark.asyncio
    async def test_get_directories(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)

        # Act
        result = await authorized_http_client.get_directories(test_repo, dir_path)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).contains_item(lambda item: item.name == dir_name)

    @pytest.mark.asyncio
    async def test_rename_directory(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)
        new_dir_name = 'pinkfloyd'

        # Act
        result = await authorized_http_client.rename_directory(test_repo, dir_path + dir_name, new_dir_name)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()

        # Save context
        self.context.add('dir_name', new_dir_name)

    @pytest.mark.asyncio
    async def test_get_directories_recursive(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)

        # Act
        result = await authorized_http_client.get_directories(test_repo, dir_path, recursive=True)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).contains_item(lambda item: item.name == dir_name)
        assert_that(result.content[0].parent_dir).is_not_none().is_not_empty()

    @pytest.mark.asyncio
    async def test_get_directory_detail(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)

        # Act
        result = await authorized_http_client.get_directory_detail(test_repo, dir_path + dir_name)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_instance_of(DirectoryItemDetail)

    @pytest.mark.asyncio
    async def test_delete_directory(self, test_repo, authorized_http_client):
        # Arrange
        dir_path = self.context.typed_get('dir_path', str)
        dir_name = self.context.typed_get('dir_name', str)

        # Act
        result = await authorized_http_client.delete_directory(test_repo, dir_path + dir_name)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()
