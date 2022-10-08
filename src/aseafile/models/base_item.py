from ..enums import ItemType
from pydantic import BaseModel


class BaseItem(BaseModel):
    """Model with information about the seafile item (repo, file, directory ...)"""
    id: str
    type: ItemType
    name: str
    mtime: int
    permission: str
