from fastapi.testclient import TestClient

from BACKEND_NAME_PLACEHOLDER.main import app

client = TestClient(app)


def test_create_person():
    response = client.post("/person/", json={"first_name": "Max", "name": "Mustermann"})

    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["first_name"] == "Max"
    assert data["last_name"] == "Mustermann" or data.get("name") == "Mustermann"


def test_get_person_by_id():
    create = client.post("/person/", json={"first_name": "Anna", "name": "Schmidt"})

    assert create.status_code == 200
    person_id = create.json()["id"]

    response = client.get(f"/person/{person_id}")

    assert response.status_code == 200
    assert response.json()["id"] == person_id


def test_get_person_not_found():
    response = client.get("/person/999999")
    assert response.status_code == 404


def test_update_person():
    created = client.post("/person/", json={"first_name": "Tom", "name": "Old"})

    person = created.json()

    response = client.put(
        "/person/", json={"id": person["id"], "first_name": "Tom", "name": "New"}
    )

    assert response.status_code in [200, 204]

    updated = client.get(f"/person/{person['id']}")

    assert updated.status_code == 200
    assert updated.json().get("name") == "New"


def test_delete_person():
    created = client.post("/person/", json={"first_name": "Delete", "name": "Me"})

    person_id = created.json()["id"]

    response = client.delete(f"/person/{person_id}/")
    assert response.status_code in [200, 204]

    check = client.get(f"/person/{person_id}")
    assert check.status_code == 404


def test_invalid_person_payload():
    response = client.post("/person/", json={})
    assert response.status_code == 422
