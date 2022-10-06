from .base import StrEnum


class FileOperation(StrEnum):
    """Enumeration of operations that can be performed on files"""

    CREATE = 'create'

    RENAME = 'rename'

    LOCK = 'lock'

    UNLOCK = 'unlock'

    MOVE = 'move'

    COPY = 'copy'

    DELETE = 'delete'
