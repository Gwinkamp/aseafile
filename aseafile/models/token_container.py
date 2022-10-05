from pydantic import BaseModel


class TokenContainer(BaseModel):
    token: str
