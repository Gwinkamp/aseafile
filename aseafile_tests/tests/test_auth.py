import pytest
from http import HTTPStatus
from pydantic import HttpUrl
from assertpy import assert_that
from aseafile import SeafileHttpClient
from aseafile.models import TokenContainer
from aseafile_tests.config import SETTINGS
from aseafile_tests.test_data.context import TestContext

# Scenarios
from aseafile_tests.test_data.scenarios import FAILED_OBTAIN_AUTH_TOKEN_SCENARIOS


@pytest.mark.incremental
class TestCreateHttpClientAndPing:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('baseUrl', SETTINGS.base_url)

    def test_create_instance(self):
        # Arrange
        base_url = self.context.typed_get('baseUrl', HttpUrl)

        # Act
        http_client = SeafileHttpClient(base_url)

        # Assert
        assert_that(http_client).is_not_none()

        # Save context
        self.context.add('httpClient', http_client)

    @pytest.mark.asyncio
    async def test_ping(self):
        # Arrange
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.ping()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_equal_to('pong')


@pytest.mark.incremental
class TestSuccessObtainAuthTokenAndPing:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('baseUrl', SETTINGS.base_url)
        self.context.add('email', SETTINGS.email)
        self.context.add('password', SETTINGS.password)

    def test_create_instance(self):
        # Arrange
        base_url = self.context.typed_get('baseUrl', HttpUrl)

        # Act
        http_client = SeafileHttpClient(base_url)

        # Assert
        assert_that(http_client).is_not_none()

        # Save context
        self.context.add('httpClient', http_client)

    @pytest.mark.asyncio
    async def test_obtain_auth_token(self):
        # Arrange
        email = self.context.typed_get('email', str)
        password = self.context.typed_get('password', str)
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.obtain_auth_token(email, password)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_instance_of(TokenContainer)

        # Save context
        self.context.add('token', result.content.token)

    @pytest.mark.asyncio
    async def test_auth_ping(self):
        # Arrange
        token = self.context.typed_get('token', str)
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.auth_ping(token)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_equal_to('pong')


@pytest.mark.incremental
@pytest.mark.usefixtures("use_custom_assertions")
class TestFailedObtainAuthToken:
    SCENARIOS = FAILED_OBTAIN_AUTH_TOKEN_SCENARIOS

    def setup_class(self):
        self.base_url = SETTINGS.base_url

    def test_create_instance(self, context: TestContext):
        # Act
        http_client = SeafileHttpClient(self.base_url)

        # Assert
        assert_that(http_client).is_not_none()

        # Save context
        context.add('httpClient', http_client)

    @pytest.mark.asyncio
    async def test_obtain_auth_token(self, context: TestContext):
        # Arrange
        email = context.typed_get('email', str)
        password = context.typed_get('password', str)
        http_client = context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.obtain_auth_token(email, password)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_false()
        assert_that(result.status).is_equal_to(HTTPStatus.BAD_REQUEST)
        assert_that(result.content).is_none()
        assert_that(result.errors).is_not_none().is_not_empty()
        assert_that(result.errors).contains_item(lambda e: e.message == 'Unable to login with provided credentials.')


@pytest.mark.incremental
@pytest.mark.usefixtures("use_custom_assertions")
class TestFailedAuthPingWithoutToken:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('token', 'failed_token')
        self.context.add('httpClient', SeafileHttpClient(SETTINGS.base_url))

    @pytest.mark.asyncio
    async def test_obtain_auth_token(self):
        # Arrange
        token = self.context.typed_get('token', str)
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.auth_ping(token)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_false()
        assert_that(result.status).is_equal_to(HTTPStatus.UNAUTHORIZED)
        assert_that(result.content).is_none()
        assert_that(result.errors).is_not_none().is_not_empty()
        assert_that(result.errors).contains_item(lambda e: e.message == 'Invalid token')


@pytest.mark.incremental
class TestAuthorizeAndAutosaveToken:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('email', SETTINGS.email)
        self.context.add('password', SETTINGS.password)
        self.context.add('httpClient', SeafileHttpClient(SETTINGS.base_url))

    @pytest.mark.asyncio
    async def test_authorize(self):
        # Arrange
        email = self.context.typed_get('email', str)
        password = self.context.typed_get('password', str)
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        await http_client.authorize(email, password)

        # Assert
        assert_that(http_client.token).is_not_none().is_not_empty()

    @pytest.mark.asyncio
    async def test_auth_ping(self):
        # Arrange
        http_client = self.context.typed_get('httpClient', SeafileHttpClient)

        # Act
        result = await http_client.auth_ping()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_equal_to('pong')
