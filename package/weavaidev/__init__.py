from pydantic import BaseModel


class Config(BaseModel):
    auth_token: str
    env: str
