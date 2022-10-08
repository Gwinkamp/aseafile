from pydantic import BaseModel


class UploadedFileItem(BaseModel):
    id: str
    name: str
    size: int
