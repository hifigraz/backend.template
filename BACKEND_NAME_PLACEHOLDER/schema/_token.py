from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str | None = None


class LoginRequest(BaseModel):

    user_name: str
    password: str