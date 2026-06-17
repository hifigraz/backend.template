import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.status import HTTP_401_UNAUTHORIZED

from ..crud import Crud
from ..schema import UserFilter

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_ALGORITHM = "HS256"
_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def define_routes(app: FastAPI, crud: Crud) -> None:

    @app.post("/auth/login", response_model=TokenResponse)
    async def login(  # pyright: ignore[reportUnusedFunction]
        credentials: LoginRequest,
    ) -> TokenResponse:
        users = crud.get_users(UserFilter(user_name=credentials.username))
        if not users or not _pwd_context.verify(credentials.password, users[0].password_hash):
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        token = jwt.encode({"sub": users[0].user_name, "exp": expire}, _SECRET_KEY, algorithm=_ALGORITHM)
        return TokenResponse(access_token=token, token_type="bearer")
