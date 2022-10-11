class RouteStorage:
    """Route storage for storing, processing and giving routes of seafile web api"""

    DEFAULT_SUFFIX = 'api2/'

    PING_ROUTE = 'ping/'
    AUTH_PING_ROUTE = 'auth/ping'
    AUTH_TOKEN_ROUTE = 'auth-token/'
    REPO_ROUTE = 'repos/'
    DEFAULT_REPO_ROUTE = 'default-repo/'
    DIR_ROUTE = 'repos/{repo_id}/dir/'
    FILE_ROUTE = 'repos/{repo_id}/file/'
    SMART_LINK_ROUTE = 'smart-link/'
    GET_UPLOAD_LINK_ROUTE = 'repos/{repo_id}/upload-link/'
    SEARCH_ROUTE = 'search-file/'

    def __init__(self, version: str = 'v2.1', suffix: str | None = None):
        self._version = version
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

    @property
    def repos(self):
        return self._suffix + self.REPO_ROUTE

    @property
    def default_repo(self):
        return self._suffix + self.DEFAULT_REPO_ROUTE

    @property
    def smart_link(self):
        return 'api/' + self._version + '/' + self.SMART_LINK_ROUTE

    @property
    def search_file(self):
        return 'api/' + self._version + '/' + self.SEARCH_ROUTE

    def repo(self, repo_id: str):
        return self._suffix + self.REPO_ROUTE + repo_id + '/'

    def file(self, repo_id: str):
        return self._suffix + self.FILE_ROUTE.format(repo_id=repo_id)

    def file_detail(self, repo_id: str):
        return self._suffix + self.FILE_ROUTE.format(repo_id=repo_id) + 'detail/'

    def dir(self, repo_id: str):
        return self._suffix + self.DIR_ROUTE.format(repo_id=repo_id)

    def dir_detail(self, repo_id: str):
        return 'api/' + self._version + '/' + self.DIR_ROUTE.format(repo_id=repo_id) + 'detail/'

    def get_upload_link(self, repo_id: str):
        return self._suffix + self.GET_UPLOAD_LINK_ROUTE.format(repo_id=repo_id)
