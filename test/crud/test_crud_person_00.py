from .. import test_module

Crud = test_module.crud.Crud
PersonBase = test_module.schema.PersonBase
PersonFull = test_module.schema.PersonFull
PersonFilter = test_module.schema.PersonFilter

get_engine = test_module.engine.get_engine


def test_create_person():
    crud = Crud(get_engine())
    person = crud.create_person(PersonBase(first_name="John", last_name="Doe"))
    assert type(person) == PersonFull
    assert person.id
    assert person.first_name == "John"
    assert person.last_name == "Doe"


def test_get_persons():
    crud = Crud(get_engine())
    crud.create_person(PersonBase(first_name="John", last_name="Doe"))
    persons = crud.get_persons()
    assert len(persons) == 1
    assert persons[0].first_name == "John"
    assert persons[0].last_name == "Doe"


def test_change_person():
    crud = Crud(get_engine())
    person = crud.create_person(PersonBase(first_name="John", last_name="Doe"))
    crud.change_person(PersonFull(id=person.id, first_name="Johnny", last_name="Smith"))
    persons = crud.get_persons(PersonFilter(id=person.id))
    assert len(persons) == 1
    assert persons[0].first_name == "Johnny"
    assert persons[0].last_name == "Smith"


def test_delete_person():
    crud = Crud(get_engine())
    person = crud.create_person(PersonBase(first_name="Jane", last_name="Roe"))
    crud.delete_person(person.id)
    assert crud.get_persons() == []
