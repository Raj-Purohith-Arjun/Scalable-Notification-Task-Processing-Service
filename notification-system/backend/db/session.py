import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


def _make_engine():
    from backend.config import settings
    return create_async_engine(settings.DATABASE_URL, echo=False)


def _make_session_factory(eng):
    return sessionmaker(bind=eng, class_=AsyncSession, expire_on_commit=False)


# lazy init
engine = _make_engine()
AsyncSessionLocal = _make_session_factory(engine)


async def get_db():
    # yield session
    async with AsyncSessionLocal() as session:
        yield session
