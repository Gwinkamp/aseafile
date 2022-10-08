from .base import StrEnum


class ItemType(StrEnum):
    """Enumeration of item types"""
    FILE = 'file'
    REPOSITORY = 'repo'
    DIRECTORY = 'dir'
