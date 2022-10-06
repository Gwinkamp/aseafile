from .base import StrEnum


class ItemType(StrEnum):
    REPO = 'repo'
    FILE = 'file'
    DIR = 'dir'
