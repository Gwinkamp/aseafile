from pydantic import BaseModel


class SmartLink(BaseModel):
    """Model with information about the seafile smart-link"""
    smart_link: str
    smart_link_token: str
    name: str
