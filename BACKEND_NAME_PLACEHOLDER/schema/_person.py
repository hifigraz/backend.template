from pydantic import BaseModel


class PersonBase(BaseModel):
    first_name: str
    name: str


class PersonFull(PersonBase):
    id: int


class PersonFilter(BaseModel):
    first_name: str | None = None
    name: str | None = None
    id: int | None = None
