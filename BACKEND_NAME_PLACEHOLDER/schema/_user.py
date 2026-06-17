"""
Module containing User data models for application.

This module defines the structure of user data:
    - UserBase: common attributes (user_name, name, password_hash)
    - UserFull: UserBase + id (internal use, contains the hash)
    - UserCreate: registration payload with a *plain* password
    - UserPublic: safe representation returned by the API (no hash)
    - UserFilter: filter object for queries
"""

from pydantic import BaseModel


class UserBase(BaseModel):
    """
    Base structure of a User as stored in the database.

    Attributes:
        user_name (str): The username for the user.
        name (str): The full name of the user.
        password_hash (str): The hashed password of the user.
    """

    user_name: str
    name: str
    password_hash: str


class UserFull(UserBase):
    """
    Complete User object including the database id.

    Attributes:
        id (int): The unique identifier for the user.
    """

    id: int


class UserCreate(BaseModel):
    """
    Payload to register a new user. Contains the *plain* password,
    which is hashed by the service layer before storage.

    Attributes:
        user_name (str): The username for the new user.
        name (str): The full name of the new user.
        password (str): The plain (un-hashed) password.
    """

    user_name: str
    name: str
    password: str


class UserPublic(BaseModel):
    """
    Public representation of a user, safe to return via the API.
    Deliberately omits the password hash.

    Attributes:
        id (int): The unique identifier for the user.
        user_name (str): The username.
        name (str): The full name.
    """

    id: int
    user_name: str
    name: str


class UserFilter(BaseModel):
    """
    Represents a filter for users.

    Attributes:
        user_name (str | None): The username to filter by.
        name (str | None): The name to filter by.
        id (int | None): The id to filter by.
        use_and (bool): Whether to combine multiple filters with 'AND' (default: True).
    """

    user_name: str | None = None
    name: str | None = None
    id: int | None = None
    use_and: bool = True