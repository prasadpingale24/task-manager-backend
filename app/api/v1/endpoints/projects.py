from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from datetime import datetime

from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.core.dependencies import get_current_user
from app.models.user import User

from app.services.project_service import (
    create_project_service,
    get_user_projects,
    get_project_by_id,
    update_project_service,
    delete_project_service
)
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectResponse,
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = create_project_service(db, payload, current_user)

    return project

@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_project(db, project_in, current_user)


@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),):
    return get_user_projects(db, current_user)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project = get_project_by_id(db, project_id, current_user)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project = update_project_service(
            db, project_id, payload, current_user
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project",
        )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = delete_project_service(
            db, project_id, current_user
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project",
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return None
