import os

# worker settings
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "task_queue")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/taskdb",
)
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "4"))
METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
