from strenum import StrEnum


class DirectoryOperation(StrEnum):
    """Enumeration of operations that can be performed on directories"""

    CREATE = 'mkdir'

    RENAME = 'rename'
