"""
Module containing Person data models for application.

This module defines two classes: PersonBase and PersonFull, both derived from Pydantic BaseModel.
These classes represent the structure of person data in the application, with PersonBase as a base model
containing common attributes like first_name, name, and password_hash, and PersonFull extending it by
adding an id attribute.
"""

from pydantic import BaseModel


class PersonBase(BaseModel):
  

    first_name: str
    last_name: str


class PersonFull(PersonBase):
    """
    Represents a complete Person object in the application, inheriting from PersonBase and adding an
    id attribute.

    Attributes:
        id (int): The unique identifier for the person.
    """

    id: int


class PersonFilter(BaseModel):
    """
    Represents a filter for persons.

    Attributes:
        person_name (str | None): The personname of the person to filter by.
        name (str | None): The name of the person to filter by.
        id (str | None): The ID of the person to filter by.
        use_and (bool): Determines whether to use 'AND' operator for multiple filters (Default: True).
    """

    first_name: str | None = None
    last_name: str | None = None
    id: int | None = None
    use_and: bool = True
