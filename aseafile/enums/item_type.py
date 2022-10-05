from strenum import StrEnum


class ItemType(StrEnum):
    REPO = 'repo'
    FILE = 'file'
    DIR = 'dir'
