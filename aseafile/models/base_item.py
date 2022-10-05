from aseafile.enums import ItemType
from pydantic import BaseModel


class BaseItem(BaseModel):
    id: str
    type: ItemType
    name: str
    mtime: int
    permission: str
