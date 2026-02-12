from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    status: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    return {
        "id": "task-456",
        "project_id": payload.project_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status,
        "created_at": "2026-02-13T12:00:00Z",
        "updated_at": "2026-02-13T12:00:00Z"
    }


@router.get("/", response_model=List[dict])
def list_tasks():
    return [
        {
            "id": "task-456",
            "project_id": "proj-123",
            "title": "Setup backend",
            "description": "Initial placeholder task",
            "status": "ACTIVE",
            "created_at": "2026-02-13T12:00:00Z",
            "updated_at": "2026-02-13T12:00:00Z"
        }
    ]


@router.patch("/{task_id}")
def update_task(task_id: str, payload: TaskUpdate):
    return {
        "id": task_id,
        "updated_fields": payload.dict(exclude_none=True),
        "updated_at": "2026-02-13T13:00:00Z"
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    return None
