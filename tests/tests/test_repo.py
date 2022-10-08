import pytest
from http import HTTPStatus
from assertpy import assert_that
from src.aseafile.models import RepoItem
from tests.test_data.context import TestContext


@pytest.mark.incremental
@pytest.mark.usefixtures("use_custom_assertions")
class TestRepoManagement:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('repo_name', 'test_repo')

    @pytest.mark.asyncio
    async def test_create_repo(self, authorized_http_client):
        # Arrange
        repo_name = self.context.typed_get('repo_name', str)

        # Act
        result = await authorized_http_client.create_repo(repo_name)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none()
        assert_that(result.content).is_instance_of(RepoItem)
        assert_that(result.content.name).is_equal_to(repo_name)

        # Save context
        self.context.add('repo_id', result.content.id)

    @pytest.mark.asyncio
    async def test_get_repos(self, authorized_http_client):
        # Arrange
        repo_id = self.context.typed_get('repo_id', str)

        # Act
        result = await authorized_http_client.get_repos()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).contains_item(lambda item: item.id == repo_id)

    @pytest.mark.asyncio
    async def test_delete_repo(self, authorized_http_client):
        # Arrange
        repo_id = self.context.typed_get('repo_id', str)

        # Act
        result = await authorized_http_client.delete_repo(repo_id)

        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_none()


@pytest.mark.incremental
class TestDefaultRepoManagement:

    def setup_class(self):
        self.context = TestContext()

    @pytest.mark.asyncio
    async def test_create_default_repo(self, authorized_http_client):
        # Act
        result = await authorized_http_client.create_default_repo()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none()
        assert_that(result.content).is_instance_of(str)

        # Save context
        self.context.add('default_repo_id', result.content)

    @pytest.mark.asyncio
    async def test_get_default_repo(self, authorized_http_client):
        # Arrange
        default_repo_id = self.context.typed_get('default_repo_id', str)

        # Act
        result = await authorized_http_client.get_default_repo()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.errors).is_none()
        assert_that(result.content).is_not_none()
        assert_that(result.content).is_equal_to(default_repo_id)
