from pydantic import BaseModel


class SmartLink(BaseModel):
    smart_link: str
    smart_link_token: str
    name: str
