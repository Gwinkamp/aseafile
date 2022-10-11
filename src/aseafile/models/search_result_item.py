from datetime import datetime
from pydantic import BaseModel
from ..enums import ItemType


class SearchResultItem(BaseModel):
    path: str
    size: int
    mtime: datetime
    type: ItemType
