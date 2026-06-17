import pytest

from BACKEND_NAME_PLACEHOLDER.config import Config
from BACKEND_NAME_PLACEHOLDER.service import Auth
from BACKEND_NAME_PLACEHOLDER.utils._seed_admin import ensure_admin


def test_ensure_admin_creates_admin(crud):
    assert crud.get_user_by_name("admin") is None
    ensure_admin(crud)
    admin = crud.get_user_by_name("admin")
    assert admin is not None
    assert admin.user_name == "admin"
    assert Auth.verify_password("adminpass", admin.password_hash)


def test_ensure_admin_is_idempotent(crud):
    ensure_admin(crud)
    ensure_admin(crud)  # second call must not raise or duplicate
    from BACKEND_NAME_PLACEHOLDER.schema import UserFilter

    assert len(crud.get_users(UserFilter(user_name="admin"))) == 1


def test_ensure_admin_without_password_raises(crud, monkeypatch):
    # force the configured admin_password to be empty
    monkeypatch.setattr(Config.get_instance(), "_admin_password", None)
    with pytest.raises(RuntimeError):
        ensure_admin(crud)