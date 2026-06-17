import importlib
import os
import tempfile

import pytest
from fastapi import FastAPI 
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from .. import test_module

model = test_module.model
Crud = test_module.crud.Crud
UserBase = test_module.schema.UserBase


@pytest.fixture(scope="module")
def client():
    tmp_dir = tempfile.mkdtemp()
    test_db = os.path.join(tmp_dir, "test_user.db")
    engine = create_engine(f"sqlite:///{os.path.abspath(test_db)}")
    model.Base.metadata.create_all(engine)
    crud = Crud(engine)
    app = FastAPI()
    routes = importlib.import_module(test_module.__name__ + ".api._routes")
    routes.define_routes(app, crud)
    yield TestClient(app)
    engine.dispose()
    os.remove(test_db)
    os.removedirs(tmp_dir)


def test_user_post(client: TestClient):
    response = client.post("/user/", json={
        "user_name": "alice",
        "name": "Alice Muster",
        "password_hash": "geheim"
    })
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["user_name"] == "alice"
    assert data["name"] == "Alice Muster"
    assert data["id"]


def test_user_post_duplicate(client: TestClient):
    client.post("/user/", json={
        "user_name": "bob",
        "name": "Bob Muster",
        "password_hash": "geheim"
    })
    response = client.post("/user/", json={
        "user_name": "bob",
        "name": "Bob Muster",
        "password_hash": "geheim"
    })
    assert response.status_code == HTTP_409_CONFLICT


def test_user_get_all(client: TestClient):
    response = client.get("/user/")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_user_get_by_id(client: TestClient):
    create = client.post("/user/", json={
        "user_name": "charlie",
        "name": "Charlie Muster",
        "password_hash": "geheim"
    })
    user_id = create.json()["id"]
    response = client.get(f"/user/{user_id}")
    assert response.status_code == HTTP_200_OK
    assert response.json()["user_name"] == "charlie"


def test_user_get_by_id_not_found(client: TestClient):
    response = client.get("/user/99999")
    assert response.status_code == HTTP_404_NOT_FOUND


def test_user_put(client: TestClient):
    create = client.post("/user/", json={
        "user_name": "dave",
        "name": "Dave Alt",
        "password_hash": "geheim"
    })
    user_data = create.json()
    user_data["name"] = "Dave Neu"
    response = client.put("/user/", json=user_data)
    assert response.status_code == HTTP_200_OK


def test_user_delete(client: TestClient):
    create = client.post("/user/", json={
        "user_name": "eve",
        "name": "Eve Muster",
        "password_hash": "geheim"
    })
    user_id = create.json()["id"]
    response = client.delete(f"/user/{user_id}/")
    assert response.status_code == HTTP_200_OK
    check = client.get(f"/user/{user_id}")
    assert check.status_code == HTTP_404_NOT_FOUND
