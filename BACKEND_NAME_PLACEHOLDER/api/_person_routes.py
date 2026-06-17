from fastapi import FastAPI, HTTPException, status
from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from ..config import get_logger
from ..crud import Crud
from ..schema import EntityFilter, PersonBase, PersonFilter, PersonFull

log = get_logger()


def define_routes(app: FastAPI, crud: Crud) -> None:

    @app.post(path="/person/")
    async def post_person(  # pyright: ignore[reportUnusedFunction]
        person: PersonBase,
    ) -> PersonFull:
        try:
            return crud.create_person(person)
        except AttributeError as err:
            log.error(str(err))
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))

    @app.post(path="/person/{entity_id}")
    async def post_person_existing_entity(  # pyright: ignore[reportUnusedFunction]
        entity_id: int,
        person: PersonBase,
    ) -> PersonFull:
        try:
            entity_filter = EntityFilter(id=entity_id)
            entity = crud.get_entities(entity_filter)
            if len(entity) != 1:
                raise HTTPException(
                    HTTP_404_NOT_FOUND, detail="ENTITY(%d) not found" % entity_id
                )
            new_person = crud.create_person(person, entity[0])
            return new_person
        except AttributeError as error:
            log.error(dir(error))
            log.error(error)
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=error)

    @app.get(path="/person/")
    async def get_person(  # pyright: ignore[reportUnusedFunction]
        filter: str | None = None,
    ):
        return crud.get_persons(PersonFilter(name=filter))

    @app.get(path="/person/{id}")
    async def get_user_by_id(  # pyright: ignore[reportUnusedFunction]
        id: int,
    ):
        filter = PersonFilter(id=id)
        result = crud.get_persons(filter)
        if len(result) != 1:
            raise HTTPException(status_code=404, detail=f"No Person with id {id}")
        return result[0]

    @app.put(path="/person/")
    async def _put_user(person: PersonFull):  # pyright: ignore[reportUnusedFunction]
        try:
            crud.change_person(person)
        except AttributeError as error:
            raise HTTPException(status_code=404, detail=str(error))

    @app.delete(path="/person/{id}/")
    async def _delete_person(id: int):  # pyright: ignore[reportUnusedFunction]
        try:
            return crud.delete_person(id)
        except AttributeError as error:
            log.error(error)
            return HTTPException(status_code=404, detail=f"No Person with id {id}")
