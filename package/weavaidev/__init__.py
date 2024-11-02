from pydantic import BaseModel, SecretStr


class Config(BaseModel):
    auth_token: SecretStr
    env: str
