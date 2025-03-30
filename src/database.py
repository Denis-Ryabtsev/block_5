import asyncio
import datetime
from typing import AsyncGenerator

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import(
    create_async_engine, async_sessionmaker
)
import redis.asyncio as aioredis
from redis.asyncio import Redis

from config import setting


class Base(DeclarativeBase):
    pass


redis_client = aioredis.Redis(
    host=setting.REDIS_HOST, 
    port=setting.REDIS_PORT, 
    db=0, 
    decode_responses=True
)

async_engine = create_async_engine(
    url=setting.DB_URL, echo=True, pool_size=5, max_overflow=10
)

async_session = async_sessionmaker(async_engine)

async def get_async_session() -> AsyncGenerator:
    async with async_session() as session:
        await asyncio.sleep(0)
        yield session

async def get_redis_client() -> Redis:
    return redis_client

def count_cash_time():
    now = datetime.datetime.now()
    expires = now.replace(hour=14, minute=11)

    if now >= expires:
        expires += datetime.timedelta(days=1)

    expires = int(expires.timestamp())

    return expires