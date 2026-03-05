import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from prometheus_client import Counter, Histogram, start_http_server

from worker.config import (
    REDIS_URL,
    REDIS_QUEUE,
    DATABASE_URL,
    WORKER_CONCURRENCY,
    METRICS_PORT,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# metrics
TASKS_PROCESSED = Counter("worker_tasks_processed_total", "Tasks processed", ["status"])
TASK_DURATION = Histogram("worker_task_duration_seconds", "Task processing duration")

# db engine
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def update_task_status(task_id: str, status: str, db: AsyncSession) -> None:
    # update status
    from sqlalchemy import text

    await db.execute(
        text(
            "UPDATE tasks SET status = :status, updated_at = :now WHERE id = :id"
        ),
        {"status": status, "now": datetime.now(timezone.utc), "id": uuid.UUID(task_id)},
    )
    await db.commit()


async def create_notification(task_id: str, message: str, db: AsyncSession) -> None:
    # store notification
    from sqlalchemy import text

    await db.execute(
        text(
            "INSERT INTO notifications (id, task_id, message, sent_at) "
            "VALUES (:id, :task_id, :message, :now)"
        ),
        {
            "id": uuid.uuid4(),
            "task_id": uuid.UUID(task_id),
            "message": message,
            "now": datetime.now(timezone.utc),
        },
    )
    await db.commit()


async def process_job(job: dict) -> None:
    task_id = job["task_id"]
    title = job.get("title", "")
    logger.info("processing %s", task_id)

    async with AsyncSessionLocal() as db:
        try:
            await update_task_status(task_id, "processing", db)

            # simulate work
            await asyncio.sleep(1)

            await update_task_status(task_id, "completed", db)
            await create_notification(
                task_id,
                f"Task '{title}' completed successfully.",
                db,
            )
            TASKS_PROCESSED.labels(status="completed").inc()
            logger.info("completed %s", task_id)
        except Exception as exc:
            logger.error("failed %s: %s", task_id, exc)
            await update_task_status(task_id, "failed", db)
            TASKS_PROCESSED.labels(status="failed").inc()


async def worker_loop(redis_client: aioredis.Redis, sem: asyncio.Semaphore) -> None:
    while True:
        try:
            _, raw = await redis_client.blpop(REDIS_QUEUE, timeout=5)
            if raw is None:
                continue
            job = json.loads(raw)
            async with sem:
                with TASK_DURATION.time():
                    await process_job(job)
        except Exception as exc:
            logger.error("loop error: %s", exc)
            await asyncio.sleep(1)


async def main() -> None:
    # start metrics
    start_http_server(METRICS_PORT)
    logger.info("metrics on :%d", METRICS_PORT)

    redis_client = await aioredis.from_url(REDIS_URL, decode_responses=True)
    sem = asyncio.Semaphore(WORKER_CONCURRENCY)

    logger.info("worker started")
    tasks = [asyncio.create_task(worker_loop(redis_client, sem)) for _ in range(WORKER_CONCURRENCY)]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
