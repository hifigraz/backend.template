import importlib
import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from sqlalchemy import create_engine
from starlette.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from .. import test_module

model = test_module.model
Crud = test_module.crud.Crud
UserBase = test_module.schema.UserBase

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="module")
def client():
    tmp_dir = tempfile.mkdtemp()
    test_db = os.path.join(tmp_dir, "test_auth.db")
    engine = create_engine(f"sqlite:///{os.path.abspath(test_db)}")
    model.Base.metadata.create_all(engine)
    crud = Crud(engine)
    crud.create_user(UserBase(
        user_name="testuser",
        name="Test User",
        password_hash=_pwd_context.hash("geheim123"),
    ))
    app = FastAPI()
    routes = importlib.import_module(test_module.__name__ + ".api._routes")
    routes.define_routes(app, crud)
    yield TestClient(app)
    engine.dispose()
    os.remove(test_db)
    os.removedirs(tmp_dir)


def test_login_success(client: TestClient):
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "geheim123",
    })
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient):
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "falsch",
    })
    assert response.status_code == HTTP_401_UNAUTHORIZED


def test_login_unknown_user(client: TestClient):
    response = client.post("/auth/login", json={
        "username": "gibtsNicht",
        "password": "geheim123",
    })
    assert response.status_code == HTTP_401_UNAUTHORIZED


