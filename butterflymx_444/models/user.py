from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str  # Hashed and base64 decoded
    salt: str  # Base64 decoded

    class Config:
        allow_mutation = False
