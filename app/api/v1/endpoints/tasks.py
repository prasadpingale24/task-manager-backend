from fastapi import APIRouter, status, Depends
from typing import List
from datetime import datetime
from app.core.dependencies import get_current_user
from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse
)

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
def create_task(payload: TaskCreate, current_user: User = Depends(get_current_user)):
    return {
        "id": "task-456",
        "project_id": payload.project_id,
        "title": payload.title,
        "description": payload.description,
        "status": payload.status,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@router.get("/", response_model=List[TaskResponse])
def list_tasks(current_user: User = Depends(get_current_user)
):
    return [
        {
            "id": "task-456",
            "project_id": "proj-123",
            "title": "Setup backend",
            "description": "Initial placeholder task",
            "status": "ACTIVE",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, payload: TaskUpdate, current_user: User = Depends(get_current_user)
):
    return {
        "id": task_id,
        "project_id": "proj-123",
        "title": payload.title or "Updated title",
        "description": payload.description or "Updated description",
        "status": payload.status or "ACTIVE",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, current_user: User = Depends(get_current_user)
):
    return None
