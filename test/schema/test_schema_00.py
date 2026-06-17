from .. import test_module

UserBase = test_module.schema.UserBase
UserFull = test_module.schema.UserFull
UserFilter = test_module.schema.UserFilter
PersonFilter = test_module.schema.PersonFilter

EntityBase = test_module.schema.EntityBase
EntityFilter = test_module.schema.EntityFilter
EntityFull = test_module.schema.EntityFull


def test_entity_00():
    entity_base = EntityBase(name="Ulmer")

    entity_base_copy: EntityBase = eval(  #  pyright: ignore [reportAny]
        repr(entity_base)
    )
    assert entity_base_copy.name == entity_base.name

    entity: EntityFull = EntityFull(id=1, name="Fritz")

    entity_copy: EntityFull = eval(repr(entity))  #  pyright: ignore [reportAny]

    assert entity_copy == entity


def test_entity_01():
    entity_filter = EntityFilter(name="%search_string%", id=1)
    entity_filter_copy = eval(repr(entity_filter))  # pyright: ignore [reportAny]
    assert entity_filter_copy == entity_filter

    entity_filter = EntityFilter(name=None, id=1)
    entity_filter_copy = eval(repr(entity_filter))  # pyright: ignore [reportAny]
    assert entity_filter_copy == entity_filter

    entity_filter = EntityFilter(name="%search_string%", id=None)
    entity_filter_copy = eval(repr(entity_filter))  # pyright: ignore [reportAny]
    assert entity_filter_copy == entity_filter


def test_user_00():
    user_filter = UserFilter(name="%search_string%", id=1)
    user_filter_copy = eval(repr(user_filter))  # pyright: ignore [reportAny]
    assert user_filter == user_filter_copy

    user_filter = UserFilter(user_name="%search_string%", id=1)
    user_filter_copy = eval(repr(user_filter))  # pyright: ignore [reportAny]
    assert user_filter == user_filter_copy

    user_filter = UserFilter(name="%search_string%", use_and=False, id=1)
    user_filter_copy = eval(repr(user_filter))  # pyright: ignore [reportAny]
    assert user_filter == user_filter_copy

def test_person_00():
    person_filter = PersonFilter(last_name="%search_string%", id=1)
    person_filter_copy = eval(repr(person_filter))  # pyright: ignore [reportAny]
    assert person_filter == person_filter_copy

    person_filter = PersonFilter(last_name="%search_string%", id=1)
    person_filter_copy = eval(repr(person_filter))  # pyright: ignore [reportAny]
    assert person_filter == person_filter_copy

    person_filter = PersonFilter(last_name="%search_string%", use_and=False, id=1)
    person_filter_copy = eval(repr(person_filter))  # pyright: ignore [reportAny]
    assert person_filter == person_filter_copy
