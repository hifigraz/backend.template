import pytest

from BACKEND_NAME_PLACEHOLDER.schema import (
    EntityBase,
    EntityFilter,
    EntityFull,
    UserFilter,
    UserFull,
)


# --- entities ---
def test_create_and_get_entity(crud):
    created = crud.create_entity(EntityBase(name="Acme"))
    assert created.id is not None
    assert created.name == "Acme"

    fetched = crud.get_entities(EntityFilter(id=created.id))
    assert len(fetched) == 1
    assert fetched[0].name == "Acme"


def test_change_entity(crud):
    created = crud.create_entity(EntityBase(name="Old"))
    crud.change_entity(EntityFull(id=created.id, name="New"))
    fetched = crud.get_entities(EntityFilter(id=created.id))
    assert fetched[0].name == "New"


def test_change_entity_unknown_id_raises(crud):
    with pytest.raises(AttributeError):
        crud.change_entity(EntityFull(id=9999, name="Nope"))


def test_delete_entity(crud):
    created = crud.create_entity(EntityBase(name="Temp"))
    crud.delete_entity(created.id)
    assert crud.get_entities(EntityFilter(id=created.id)) == []


def test_delete_entity_unknown_id_raises(crud):
    with pytest.raises(AttributeError):
        crud.delete_entity(9999)


# --- users ---
def test_create_user_creates_entity_and_user(crud, make_user):
    user = make_user("alice", "pw", name="Alice")
    assert isinstance(user, UserFull)
    assert user.user_name == "alice"
    assert user.name == "Alice"
    assert user.id is not None


def test_get_user_by_name(crud, make_user):
    make_user("bob", "pw")
    found = crud.get_user_by_name("bob")
    assert found is not None
    assert found.user_name == "bob"


def test_get_user_by_name_unknown_returns_none(crud):
    assert crud.get_user_by_name("ghost") is None


def test_get_users_filter_by_name(crud, make_user):
    make_user("carol", "pw")
    result = crud.get_users(UserFilter(user_name="carol"))
    assert len(result) == 1
    assert result[0].user_name == "carol"


def test_get_users_filter_by_id(crud, make_user):
    user = make_user("dave", "pw")
    result = crud.get_users(UserFilter(id=user.id))
    assert len(result) == 1
    assert result[0].user_name == "dave"


def test_duplicate_user_raises(crud, make_user):
    make_user("erin", "pw")
    with pytest.raises(AttributeError):
        make_user("erin", "pw2")


def test_delete_user(crud, make_user):
    user = make_user("frank", "pw")
    crud.delete_user(user.id)
    assert crud.get_user_by_name("frank") is None


def test_delete_user_unknown_raises(crud):
    with pytest.raises(AttributeError):
        crud.delete_user(9999)
