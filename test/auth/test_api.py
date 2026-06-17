"""
HTTP-level tests. Require httpx (FastAPI TestClient dependency), which is not a
project dependency. Skipped automatically if httpx is not installed.
"""

import pytest

try:
    from fastapi.testclient import TestClient
except Exception:
    pytest.skip(
        "fastapi TestClient requires httpx (not a project dependency)",
        allow_module_level=True,
    )

import BACKEND_NAME_PLACEHOLDER.api._app as appmod  # noqa: E402


@pytest.fixture
def client(crud, admin):
    # rebuild the global app bound to the test crud (admin already seeded)
    appmod._app = None
    appmod._crud = None
    app = appmod.build_app(crud=crud)
    yield TestClient(app)
    appmod._app = None
    appmod._crud = None


def _login(client, user="admin", pw="adminpass"):
    return client.post("/token", json={"user_name": user, "password": pw})


def test_token_success(client):
    resp = _login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_token_wrong_password(client):
    resp = _login(client, pw="wrong")
    assert resp.status_code == 401


def test_token_form_data_is_rejected(client):
    # the endpoint expects JSON, not OAuth2 form data -> 422
    resp = client.post("/token", data={"username": "admin", "password": "adminpass"})
    assert resp.status_code == 422


def test_users_me_requires_auth(client):
    resp = client.get("/users/me")
    assert resp.status_code in (401, 403)  # HTTPBearer: missing credentials


def test_users_me_with_token(client):
    token = _login(client).json()["access_token"]
    resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["user_name"] == "admin"
    assert "password_hash" not in body  # UserPublic must not leak the hash


def test_register_as_admin(client):
    token = _login(client).json()["access_token"]
    resp = client.post(
        "/auth/register",
        json={"user_name": "newbie", "name": "New Bie", "password": "pw"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["user_name"] == "newbie"


def test_register_then_login_as_new_user(client):
    token = _login(client).json()["access_token"]
    client.post(
        "/auth/register",
        json={"user_name": "newbie", "name": "New Bie", "password": "pw"},
        headers={"Authorization": f"Bearer {token}"},
    )
    resp = _login(client, user="newbie", pw="pw")
    assert resp.status_code == 200