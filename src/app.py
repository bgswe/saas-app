import asyncio
import time

import asyncpg
import bcrypt
import jwt
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from cosmos.message_bus import MessageBus, Message
from cosmos.unit_of_work import AsyncUnitOfWorkFactory
from cosmos.contrib.pg.async_uow import AsyncUnitOfWorkPostgres

from repository import OrganizationRepository
from commands import Login, Signup, COMMAND_HANDLERS


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def create_database_pool():
    app.pool = await asyncpg.create_pool(
        database='saas_application',
        user='postgres',
    )


@app.on_event("shutdown")
async def close_database_pool():
    await app.pool.close()


async def app_handle(message: Message):
    async with app.pool.acquire() as connection:
        mb = MessageBus(
            uow_factory=AsyncUnitOfWorkFactory[AsyncUnitOfWorkPostgres](
                uow_cls=AsyncUnitOfWorkPostgres,
                repository_cls=OrganizationRepository,
                uow_kwargs={"connection": connection},
                repository_kwargs={"connection": connection},
            ), 
            command_handlers=COMMAND_HANDLERS,
        )

        await mb.handle(message=message)


@app.post("/command/signup/")
async def root(command: Signup):

    await app_handle(message=command)

    return {"message": "signup initiated"}


@app.post("/command/login/")
async def login(command: Login):
    """Strange handling here because it's a quick authentication, but users live inside 
    organization AggregateRoot. It's also not a mutation, so it's more like a view,
    than like a command. This implementation should serve all login needs, can revisit 
    at a later date.
    """

    async with app.pool.acquire() as connection:
        user = await connection.fetchrow(
            """
            SELECT
                *
            FROM 
                usr
            WHERE 
                email = $1;
            """,
            command.email,
        )

        failed_auth_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

        if user is None:
            raise failed_auth_exception

        is_correct = bcrypt.checkpw(
            command.password.encode("utf-8"),
            user["password_hash"].encode("utf-8"),
        )

        if not is_correct:
            raise failed_auth_exception
        
        access_token = jwt.encode(
            {
                "client_id": str(user["id"]),
                "expires": time.time() + 600,  # 10 minutes
            },
            "secret",
            algorithm="HS256",
        )

        # TODO: Generate and return valid JWT access token
        # TODO: Set httpOnly cookie containing refresh token
        return {
            "access_token": access_token,
        }

        
