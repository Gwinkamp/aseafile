class UnauthorizedError(Exception):
    """Custom exception that is raised when a token obtained error occurs"""

    def __init__(self, *args: object):
        super().__init__(*args)

        if args is not None and len(args) > 0:
            self.message = args[0] if args[0] is not None else 'The access token was not obtained'
