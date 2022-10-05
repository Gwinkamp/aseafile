from datetime import datetime
from pydantic import BaseModel


class DirectoryItemDetail(BaseModel):
    repo_id: str
    name: str
    mtime: datetime
    path: str
