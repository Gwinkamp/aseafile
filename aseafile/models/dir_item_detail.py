from datetime import datetime
from pydantic import BaseModel


class DirectoryItemDetail(BaseModel):
    """Model with detail information about the seafile directory"""
    repo_id: str
    name: str
    mtime: datetime
    path: str
