import importlib
import os
import tempfile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from .. import test_module

model = test_module.model
Crud = test_module.crud.Crud


@pytest.fixture(scope="module")
def client():
    tmp_dir = tempfile.mkdtemp()
    test_db = os.path.join(tmp_dir, "test_person.db")
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


def test_person_post(client: TestClient):
    response = client.post("/person/", json={"first_name": "John", "last_name": "Doe"})
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["id"]


def test_person_get_all(client: TestClient):
    response = client.get("/person/")
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_person_get_by_id(client: TestClient):
    create = client.post("/person/", json={"first_name": "Jane", "last_name": "Roe"})
    person_id = create.json()["id"]
    response = client.get(f"/person/{person_id}")
    assert response.status_code == HTTP_200_OK
    assert response.json()["first_name"] == "Jane"


def test_person_get_by_id_not_found(client: TestClient):
    response = client.get("/person/99999")
    assert response.status_code == HTTP_404_NOT_FOUND


def test_person_put(client: TestClient):
    create = client.post("/person/", json={"first_name": "Max", "last_name": "Alt"})
    person = create.json()
    person["last_name"] = "Neu"
    response = client.put("/person/", json=person)
    assert response.status_code == HTTP_200_OK
    check = client.get(f"/person/{person['id']}")
    assert check.json()["last_name"] == "Neu"


def test_person_delete(client: TestClient):
    create = client.post("/person/", json={"first_name": "Eve", "last_name": "Muster"})
    person_id = create.json()["id"]
    response = client.delete(f"/person/{person_id}/")
    assert response.status_code == HTTP_200_OK
    check = client.get(f"/person/{person_id}")
    assert check.status_code == HTTP_404_NOT_FOUND
