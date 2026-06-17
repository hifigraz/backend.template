from ..config import Config
from ..crud import Crud
from ..engine import get_engine
from ..schema import UserBase
from ..service import Auth


def ensure_admin(crud: Crud | None = None) -> None:
    """
    Creates the initial admin/root user if it does not exist yet.
    User name and password are taken from the Config
    (config file keys 'admin_user'/'admin_password' or env ADMIN_USER/ADMIN_PASSWORD).

    Call this once at startup so an admin exists to register further
    users via /auth/register.
    """
    crud = crud or Crud(get_engine())
    config = Config.get_instance()
    if crud.get_user_by_name(config.admin_user):
        return
    if not config.admin_password:
        raise RuntimeError(
            "admin_password is not set (config file or ADMIN_PASSWORD env)"
        )
    crud.create_user(
        UserBase(
            user_name=config.admin_user,
            name="Administrator",
            password_hash=Auth.hash_password(config.admin_password),
        )
    )