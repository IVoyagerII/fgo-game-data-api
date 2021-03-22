from typing import Generator

from aioredis import Redis
from fastapi import Request
from sqlalchemy.engine import Connection

from ..db.engine import engines
from ..schemas.common import Region


def get_db(region: Region) -> Generator[Connection, None, None]:
    with engines[region].connect() as connection:
        yield connection


def get_db_transaction(region: Region) -> Generator[Connection, None, None]:
    with engines[region].begin() as connection:
        yield connection


def get_redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis
