from fastapi import Depends, FastAPI

from ..config import get_logger
from ..crud import Crud
from ..schema import LoginRequest, Token, UserCreate, UserFull, UserPublic
from ..service import Auth

log = get_logger()


def define_routes(app: FastAPI, crud: Crud) -> Auth:
    """
    Defines the authentication routes and returns the Auth instance so that
    other route modules can reuse `auth.get_current_user` as a dependency.
    """
    auth = Auth(crud)

    @app.post("/token")
    async def login_for_access_token(  # pyright: ignore[reportUnusedFunction]
        credentials: LoginRequest,
    ) -> Token:
        return auth.login(credentials.user_name, credentials.password)

    @app.get("/users/me")
    async def read_users_me(  # pyright: ignore[reportUnusedFunction]
        current_user: UserFull = Depends(auth.get_current_user),
    ) -> UserPublic:
        return UserPublic(
            id=current_user.id,
            user_name=current_user.user_name,
            name=current_user.name,
        )

    @app.post("/auth/register")
    async def register(  # pyright: ignore[reportUnusedFunction]
        payload: UserCreate,
        current_user: UserFull = Depends(auth.get_current_user),
    ) -> UserPublic:
        created = auth.register(payload, current_user)
        return UserPublic(
            id=created.id, user_name=created.user_name, name=created.name
        )

    return auth