from .base import StrEnum


class RepoType(StrEnum):
    """Enumeration of library types"""

    MINE = 'mine'

    SHARED = 'shared'

    GROUP = 'group'

    ORG = 'org'
