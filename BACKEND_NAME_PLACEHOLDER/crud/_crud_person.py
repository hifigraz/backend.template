from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import get_logger
from ..model import Entity, Person
from ..schema import EntityBase, EntityFull, PersonBase, PersonFilter, PersonFull
from ._crud_entity import CrudEntity
from ._error_messages import ERROR_MESSAGES

log = get_logger()
"""
CrudPerson class for managing a database of Person entities.

This class provides methods to create, read, update, and delete Person objects from the database.
The database is abstracted away, making it easy to switch between different databases or data storage solutions.

Methods:
    - get_persons(filter: str | None = None) -> list[Person]: Retrieves a list of Person entities based on a provided filter (optional). If no filter is provided, returns an empty list.
"""


class CrudPerson(CrudEntity):
    def get_persons(self, filter: PersonFilter | None = None) -> list[PersonFull]:
        with Session(bind=self._engine) as session:
            full_persons: list[PersonFull] = []
            stmt = select(Person)
            if filter and filter.name:
                stmt = stmt.where(Person.name.like(filter.name))
            if filter and filter.first_name:
                stmt = stmt.where(Person.first_name.like(filter.first_name))
            if filter and filter.id:
                stmt = stmt.where(Person.id == filter.id)

            log.debug(f"Filter:{stmt}")
            for orm_person in session.execute(stmt).scalars().all():
                full_persons.append(
                    PersonFull(
                        id=orm_person.id,
                        first_name=orm_person.first_name,
                        name=orm_person.name,
                    )
                )
            return full_persons

    def create_person(
        self, new_person: PersonBase, existing_entity: EntityFull | None = None
    ) -> PersonFull:
        with Session(bind=self._engine) as session:
            person = Person()
            person.name = new_person.name
            person.first_name = new_person.first_name

            entity: Entity | None = None
            if existing_entity:
                entity = self._get_entity(session, existing_entity)
                if not entity:
                    raise AttributeError(
                        ERROR_MESSAGES.NO_SUCH_ID
                        % (Entity.__name__, existing_entity.id)
                    )
                if new_person.name:
                    entity.name = new_person.name
            try:
                if not entity:
                    new_entity = EntityBase(name=new_person.name)
                    entity = self._create_entity(session, new_entity)

                person.entity = entity
                session.add(person)
                session.commit()
                person_full = PersonFull(
                    name=person.name,
                    first_name=person.first_name,
                    id=person.id,
                )
                return person_full
            except IntegrityError as exc:
                log.error(exc)
                log.error(exc.orig)
                raise

    def change_person(self, person: PersonFull):
        with Session(bind=self._engine) as session:
            stmt = select(Person).where(Person.id == person.id)
            result = list(session.execute(stmt).scalars())
            if len(result) != 1:
                raise AttributeError(
                    ERROR_MESSAGES.NO_SUCH_ID % (Person.__name__, person.id)
                )
            change_person = result[0]
            change_person.name = person.name
            change_person.first_name = person.first_name
            session.add(change_person)
            session.commit()

    def delete_person(self, id: int):
        with Session(bind=self._engine) as session:
            stmt = delete(Person).where(Person.id.is_(id))
            result = session.execute(stmt)
            log.error(f"Result Type is: {type(result)}")
            if (
                not result.rowcount  # pyright: ignore[reportUnknownMemberType,reportAttributeAccessIssue]
            ):
                raise AttributeError(ERROR_MESSAGES.NO_SUCH_ID % (Person.__name__, id))
            session.commit()
