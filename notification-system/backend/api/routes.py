import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas import TaskCreate, TaskResponse, TaskListResponse
from backend.db.session import get_db
import backend.services.task_service as svc

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def submit_task(body: TaskCreate, db: AsyncSession = Depends(get_db)):
    # validate + create
    task = await svc.create_task(db, body.title, body.payload, body.user_id)
    await svc.enqueue_task(str(task.id), task.title, task.payload)
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        payload=task.payload,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    # check cache first
    cached = await svc.get_cached_task(task_id)
    if cached:
        return TaskResponse(**cached)

    task = await svc.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    response = TaskResponse(
        id=str(task.id),
        title=task.title,
        payload=task.payload,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )
    await svc.cache_task(task_id, response.model_dump(mode="json"))
    return response


@router.get("/tasks", response_model=TaskListResponse)
async def list_all_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    tasks = await svc.list_tasks(db, skip=skip, limit=limit)
    items = [
        TaskResponse(
            id=str(t.id),
            title=t.title,
            payload=t.payload,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )
        for t in tasks
    ]
    return TaskListResponse(tasks=items, total=len(items))


@router.get("/health")
async def health():
    return {"status": "ok"}
