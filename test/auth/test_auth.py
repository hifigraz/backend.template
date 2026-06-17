from datetime import timedelta

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from BACKEND_NAME_PLACEHOLDER.schema import Token, UserCreate, UserFull
from BACKEND_NAME_PLACEHOLDER.service import Auth
from BACKEND_NAME_PLACEHOLDER.service.authentication import (
    ALGORITHM,
    _get_secret_key,
)


def _bearer(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


# --- password hashing ---
def test_hash_and_verify_password():
    hashed = Auth.hash_password("geheim123")
    assert hashed != "geheim123"
    assert Auth.verify_password("geheim123", hashed) is True
    assert Auth.verify_password("falsch", hashed) is False


# --- token ---
def test_create_access_token_roundtrip(auth):
    token = auth.create_access_token({"sub": "alice"})
    payload = jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
    assert payload["sub"] == "alice"
    assert "exp" in payload


# --- authenticate ---
def test_authenticate_success(auth, make_user):
    make_user("alice", "pw")
    user = auth.authenticate("alice", "pw")
    assert user is not None
    assert user.user_name == "alice"


def test_authenticate_wrong_password(auth, make_user):
    make_user("alice", "pw")
    assert auth.authenticate("alice", "wrong") is None


def test_authenticate_unknown_user(auth):
    assert auth.authenticate("ghost", "pw") is None


# --- login ---
def test_login_success(auth, make_user):
    make_user("alice", "pw")
    token = auth.login("alice", "pw")
    assert isinstance(token, Token)
    assert token.token_type == "bearer"
    assert token.access_token


def test_login_wrong_credentials_raises_401(auth, make_user):
    make_user("alice", "pw")
    with pytest.raises(HTTPException) as exc:
        auth.login("alice", "wrong")
    assert exc.value.status_code == 401


# --- get_current_user ---
def test_get_current_user_valid(auth, make_user):
    make_user("alice", "pw")
    token = auth.create_access_token({"sub": "alice"})
    user = auth.get_current_user(_bearer(token))
    assert user.user_name == "alice"


def test_get_current_user_invalid_token_raises_401(auth):
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer("not-a-real-token"))
    assert exc.value.status_code == 401


def test_get_current_user_expired_token_raises_401(auth, make_user):
    make_user("alice", "pw")
    token = auth.create_access_token({"sub": "alice"}, expires_delta=timedelta(minutes=-5))
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer(token))
    assert exc.value.status_code == 401


def test_get_current_user_unknown_subject_raises_401(auth):
    token = auth.create_access_token({"sub": "ghost"})
    with pytest.raises(HTTPException) as exc:
        auth.get_current_user(_bearer(token))
    assert exc.value.status_code == 401


# --- register (admin only) ---
def test_register_as_admin_creates_user(auth, admin, crud):
    created = auth.register(
        UserCreate(user_name="newbie", name="New Bie", password="pw"), admin
    )
    assert isinstance(created, UserFull)
    assert created.user_name == "newbie"
    # password was hashed and is verifiable
    stored = crud.get_user_by_name("newbie")
    assert Auth.verify_password("pw", stored.password_hash)


def test_register_as_non_admin_forbidden(auth, make_user):
    non_admin = make_user("bob", "pw")
    with pytest.raises(HTTPException) as exc:
        auth.register(UserCreate(user_name="x", name="x", password="pw"), non_admin)
    assert exc.value.status_code == 403


def test_register_duplicate_conflict(auth, admin):
    auth.register(UserCreate(user_name="dup", name="Dup", password="pw"), admin)
    with pytest.raises(HTTPException) as exc:
        auth.register(UserCreate(user_name="dup", name="Dup", password="pw"), admin)
    assert exc.value.status_code == 409
