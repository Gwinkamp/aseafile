from urllib.parse import urljoin


class RouteStorage:

    DEFAULT_SUFFIX = 'api2/'

    PING_ROUTE = 'ping/'
    AUTH_PING_ROUTE = 'auth/ping'
    AUTH_TOKEN_ROUTE = 'auth-token/'

    def __init__(self, suffix: str | None = None):
        self._suffix = suffix or self.DEFAULT_SUFFIX

    @property
    def ping(self):
        return self._suffix + self.PING_ROUTE

    @property
    def auth_ping(self):
        return self._suffix + self.AUTH_PING_ROUTE

    @property
    def auth_token(self):
        return self._suffix + self.AUTH_TOKEN_ROUTE
