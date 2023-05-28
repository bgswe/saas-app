from enum import StrEnum, auto
from typing import List
from uuid import UUID

import bcrypt
from cosmos.domain import AggregateRoot, Entity


class Role(StrEnum):
    USER = auto()
    SUPERUSER = auto()

class User(Entity):
    email: str
    first_name: str | None
    last_name: str | None
    roles: List[Role]
    hashed_password: str

    @classmethod
    def create(
        cls,
        *,
        id: UUID = None,
        email: str,
        password: str,
        roles: List[Role] = None,
        first_name: str = None,
        last_name: str = None,
    ):
        if roles is None:
            roles = [Role.USER]

        hashed_password = str(bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(10)))

        return Entity.create_entity(
            cls=cls,
            id=id,
            email=email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            roles=roles,
        )


class Organization(AggregateRoot):
    name: str
    address: str
    users: List[User]

    @classmethod
    def create(
        cls,
        *,
        id: UUID = None,
        name: str,
        address: str = None,
        admin_email: str,
        admin_password: str,
    ):
        initial_user = User.create(
            email=admin_email,
            password=admin_password,
            roles=[Role.SUPERUSER],
        )

        return Entity.create_entity(
            cls=cls,
            id=id,
            name=name,
            address=address,
            users=[initial_user],
        )
