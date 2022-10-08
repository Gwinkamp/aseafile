from pydantic import BaseSettings


class Settings(BaseSettings):
    base_url: str
    email: str
    password: str
