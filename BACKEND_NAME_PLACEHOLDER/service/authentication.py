from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from ..config import Config, get_logger
from ..crud import Crud
from ..schema import Token, TokenData, UserBase, UserCreate, UserFull

log = get_logger()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bearer_scheme = HTTPBearer()


def _get_secret_key() -> str:
    secret = Config.get_instance().secret_key
    if not secret:
        raise RuntimeError("secret_key is not set (config file or SECRET_KEY env)")
    return secret


class Auth:
    """
    Authentication service built on top of the engine-based Crud layer.

    Uses bcrypt for password hashing and python-jose for JWTs (HS256).
    All data access goes through the injected Crud instance; no
    request-scoped Session is needed.
    """

    def __init__(self, crud: Crud):
        self._crud = crud

    # --- password helpers (bcrypt directly; bcrypt only uses the first 72 bytes) ---
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8")[:72], bcrypt.gensalt()
        ).decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72], hashed_password.encode("utf-8")
        )

    # --- token helpers ---
    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode["exp"] = expire
        return jwt.encode(to_encode, _get_secret_key(), algorithm=ALGORITHM)

    # --- core logic ---
    def authenticate(self, user_name: str, password: str) -> UserFull | None:
        user = self._crud.get_user_by_name(user_name)
        if not user or not user.password_hash:
            return None
        if not self.verify_password(password, user.password_hash):
            return None
        return user

    def login(self, user_name: str, password: str) -> Token:
        user = self.authenticate(user_name, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = self.create_access_token(data={"sub": user.user_name})
        return Token(access_token=access_token, token_type="bearer")

    def register(self, new_user: UserCreate, current_user: UserFull) -> UserFull:
        """Create a new user. Admin only. Hashes the plain password."""
        if current_user.user_name != Config.get_instance().admin_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin can create new users",
            )
        payload = UserBase(
            user_name=new_user.user_name,
            name=new_user.name,
            password_hash=self.hash_password(new_user.password),
        )
        try:
            return self._crud.create_user(payload)
        except AttributeError as err:
            log.error(str(err))
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    # --- FastAPI dependency ---
    def get_current_user(
        self, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> UserFull:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        token = credentials.credentials
        try:
            payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
            user_name = payload.get("sub")
            if not user_name:
                raise credentials_exception
            token_data = TokenData(user_name=user_name)
        except JWTError:
            raise credentials_exception
        if token_data.user_name is None:
            raise credentials_exception
        user = self._crud.get_user_by_name(token_data.user_name)
        if user is None:
            raise credentials_exception
        return user