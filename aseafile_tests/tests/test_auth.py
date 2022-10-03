import pytest
from http import HTTPStatus
from config import SETTINGS
from assertpy import assert_that
from aseafile import SeafileHttpClient
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
        base_url = self.context.get('baseUrl')

        # Act
        http_client = SeafileHttpClient(base_url)

        # Assert
        assert_that(http_client).is_not_none()

        # Save context
        self.context.add('httpClient', http_client)

    @pytest.mark.asyncio
    async def test_ping(self):
        # Arrange
        http_client = self.context.get('httpClient')

        # Act
        result = await http_client.ping()

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_equal_to('"pong"')


@pytest.mark.incremental
class TestSuccessObtainAuthTokenAndPing:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('baseUrl', SETTINGS.base_url)
        self.context.add('email', SETTINGS.email)
        self.context.add('password', SETTINGS.password)

    def test_create_instance(self):
        # Arrange
        base_url = self.context.get('baseUrl')

        # Act
        http_client = SeafileHttpClient(base_url)

        # Assert
        assert_that(http_client).is_not_none()

        # Save context
        self.context.add('httpClient', http_client)

    @pytest.mark.asyncio
    async def test_obtain_auth_token(self):
        # Arrange
        email = self.context.get('email')
        password = self.context.get('password')
        http_client = self.context.get('httpClient')

        # Act
        result = await http_client.obtain_auth_token(email, password)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_not_none().is_not_empty()

        # Save context
        self.context.add('token', result.content)

    @pytest.mark.asyncio
    async def test_auth_ping(self):
        # Arrange
        token = self.context.get('token')
        http_client = self.context.get('httpClient')

        # Act
        result = await http_client.auth_ping(token)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_true()
        assert_that(result.errors).is_none()
        assert_that(result.status).is_equal_to(HTTPStatus.OK)
        assert_that(result.content).is_equal_to('"pong"')


@pytest.mark.incremental
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
        email = context.get('email')
        password = context.get('password')
        http_client = context.get('httpClient')

        # Act
        result = await http_client.obtain_auth_token(email, password)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_false()
        assert_that(result.status).is_equal_to(HTTPStatus.BAD_REQUEST)
        assert_that(result.content).is_none()
        assert_that(result.errors).is_not_none().is_not_empty()
        assert_that(result.errors).contains_key('non_field_errors')
        assert_that(result.errors['non_field_errors']).contains_only('Unable to login with provided credentials.')


@pytest.mark.incremental
class TestFailedAuthPingWithoutToken:

    def setup_class(self):
        self.context = TestContext()
        self.context.add('token', 'failed_token')
        self.context.add('httpClient', SeafileHttpClient(SETTINGS.base_url))

    @pytest.mark.asyncio
    async def test_obtain_auth_token(self):
        # Arrange
        token = self.context.get('token')
        http_client = self.context.get('httpClient')

        # Act
        result = await http_client.auth_ping(token)

        # Assert
        assert_that(result).is_not_none()
        assert_that(result.success).is_false()
        assert_that(result.status).is_equal_to(HTTPStatus.UNAUTHORIZED)
        assert_that(result.content).is_none()
        assert_that(result.errors).is_not_none().is_not_empty()
        assert_that(result.errors).contains_key('detail')
        assert_that(result.errors['detail']).contains_only('Invalid token')
