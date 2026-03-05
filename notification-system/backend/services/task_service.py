import json
import uuid
import logging

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.task import Task, TaskStatus

logger = logging.getLogger(__name__)

# redis client
_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(
            settings.REDIS_URL, decode_responses=True
        )
    return _redis_client


async def enqueue_task(task_id: str, title: str, payload: str | None) -> None:
    # push to queue
    r = await get_redis()
    job = json.dumps({"task_id": task_id, "title": title, "payload": payload})
    await r.rpush(settings.REDIS_QUEUE, job)
    logger.info("enqueued %s", task_id)


async def cache_task(task_id: str, data: dict) -> None:
    # cache result
    r = await get_redis()
    await r.setex(f"task:{task_id}", settings.REDIS_CACHE_TTL, json.dumps(data))


async def get_cached_task(task_id: str) -> dict | None:
    # read cache
    r = await get_redis()
    raw = await r.get(f"task:{task_id}")
    if raw:
        return json.loads(raw)
    return None


async def create_task(db: AsyncSession, title: str, payload: str | None, user_id: str | None) -> Task:
    # persist task
    task = Task(
        id=uuid.uuid4(),
        title=title,
        payload=payload,
        user_id=uuid.UUID(user_id) if user_id else None,
        status=TaskStatus.pending,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_id(db: AsyncSession, task_id: str) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == uuid.UUID(task_id)))
    return result.scalar_one_or_none()


async def list_tasks(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[Task]:
    result = await db.execute(select(Task).offset(skip).limit(limit).order_by(Task.created_at.desc()))
    return list(result.scalars().all())
