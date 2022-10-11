import pytest
import aiofiles
from http import HTTPStatus
from assertpy import assert_that
from tests.test_data.scenarios import TEST_FILES


@pytest.mark.incremental
@pytest.mark.usefixtures("use_test_directory")
@pytest.mark.usefixtures("use_custom_assertions")
class TestSearchFiles:

    def setup_class(self):
        self.test_files = TEST_FILES

    async def upload_test_files(self, test_repo, authorized_http_client):
        for test_file in self.test_files:
            async with aiofiles.open(test_file['path'], 'rb') as file:
                result = await authorized_http_client.upload(test_repo, '/test_dir', test_file['name'], file)
                assert_that(result.success).is_true()

    @pytest.mark.asyncio
    async def test_search_file_by_name(self, test_repo, authorized_http_client):
        # Arrange
        await self.upload_test_files(test_repo, authorized_http_client)

        # Act
        result = await authorized_http_client.search_file('file_1', test_repo)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none().is_length(1)
        assert_that(result.content).contains_item(lambda item: 'file_1' in item.path)

    @pytest.mark.asyncio
    async def test_search_file_by_extension(self, test_repo, authorized_http_client):
        # Act
        result = await authorized_http_client.search_file('md', test_repo)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none().is_length(1)
        assert_that(result.content).contains_item(lambda item: 'md' in item.path)

    @pytest.mark.asyncio
    async def test_search_multiple_files(self, test_repo, authorized_http_client):
        # Act
        result = await authorized_http_client.search_file('file', test_repo)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none().is_length(3)
        assert_that(result.content).contains_item(lambda item: 'file' in item.path)
