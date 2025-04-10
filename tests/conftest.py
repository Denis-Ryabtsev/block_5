import asyncio
import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from redis.asyncio import Redis

from database import Base, get_async_session, get_redis_client
from config import setting
from trading_results.models import SpimexTrading
from main import app


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

engine_test = create_async_engine(url=setting.DB_URL, echo=True)
engine_setup_db = create_async_engine(url=setting.DB_URL, echo=True)
engine_insert = create_async_engine(url=setting.DB_URL, echo=True)

session_insert = async_sessionmaker(engine_insert)
session_override_db = async_sessionmaker(engine_test)

@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_db():
    assert setting.MODE == 'TEST'

    async with engine_setup_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine_setup_db.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with session_override_db() as session:
        yield session

@pytest_asyncio.fixture
async def override_get_async_session(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def async_client(override_get_async_session):
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client


@pytest_asyncio.fixture
async def fake_redis():
    mock_redis = AsyncMock(spec=Redis)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.expireat = AsyncMock(return_value=True)
    
    return mock_redis

@pytest_asyncio.fixture(autouse=True)
async def override_get_redis(fake_redis):
    async def _override():
        return fake_redis
    
    app.dependency_overrides[get_redis_client] = _override
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def insert_data(setup_db):

    async with session_insert() as session:
        test_data = [
            SpimexTrading(
                product_id="A100ANK060F",
                oil_id="A100",
                delivery_id="ANK",
                delivery_type="F",
                date=datetime.date(2025, 1, 22)
            ),
            SpimexTrading(
                product_id="B400ANK060F",
                oil_id="A101",
                delivery_id="AAA",
                delivery_type="A",
                date=datetime.date(2025, 2, 10)
            )
        ]

        session.add_all(test_data)
        await session.commit()
