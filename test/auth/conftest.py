import os

# Auth/Config read these from the environment (or a config file) at runtime.
# Set them before the application package builds its config singleton.
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("ADMIN_USER", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "adminpass")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from BACKEND_NAME_PLACEHOLDER.crud import Crud
from BACKEND_NAME_PLACEHOLDER.model import Person, User  # noqa: F401  (register mappers)
from BACKEND_NAME_PLACEHOLDER.model._base import Base
from BACKEND_NAME_PLACEHOLDER.schema import UserBase, UserCreate, UserFull
from BACKEND_NAME_PLACEHOLDER.service import Auth


@pytest.fixture
def engine():
    """Fresh in-memory SQLite shared across sessions for one test."""
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def crud(engine):
    return Crud(engine)


@pytest.fixture
def auth(crud):
    return Auth(crud)


@pytest.fixture
def make_user(auth, crud):
    """Create a user with a hashed password; returns the created UserFull."""

    def _make(user_name: str, password: str, name: str | None = None) -> UserFull:
        return crud.create_user(
            UserBase(
                user_name=user_name,
                name=name or user_name,
                password_hash=Auth.hash_password(password),
            )
        )

    return _make


@pytest.fixture
def admin(make_user):
    """The configured admin user (user_name 'admin')."""
    return make_user("admin", "adminpass", name="Administrator")
