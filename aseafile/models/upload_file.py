from typing import TypedDict, BinaryIO


class UploadFile(TypedDict):
    filename: str
    payload: BinaryIO
