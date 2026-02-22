from fastapi import APIRouter, status, Depends, HTTPException
from typing import List, Union
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskOwnerResponse
)
from app.services.task_service import TaskService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TaskResponse)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await TaskService.create_task_service(db, payload, current_user)
        
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        
    return task


@router.get("/", response_model=List[Union[TaskOwnerResponse, TaskResponse]])
async def list_tasks(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await TaskService.get_project_tasks_service(db, project_id, current_user)


@router.get("/{task_id}", response_model=Union[TaskOwnerResponse, TaskResponse])
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await TaskService.get_task_by_id_service(db, task_id, current_user)
        
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = await TaskService.update_task_service(db, task_id, payload, current_user)
        
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await TaskService.delete_task_service(db, task_id, current_user)
        
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        
    return None
