import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from backend.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    payload: Optional[str] = None
    user_id: Optional[str] = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    payload: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int
