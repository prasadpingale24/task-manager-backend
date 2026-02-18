from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from datetime import datetime

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import (
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectMemberListResponse,
)

from app.services.project_member_service import (
    add_member_to_project,
    list_project_members,
    remove_member_from_project,
)
from app.services.project_access_service import check_project_access

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

@router.get("/{project_id}/members", response_model=list[ProjectMemberListResponse])
def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    access = check_project_access(db, project_id, current_user)

    if access is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if access is False:
        raise HTTPException(status_code=403, detail="Not authorized")

    return list_project_members(db, project_id)

@router.post(
    "/{project_id}/members",
    status_code=201,
    response_model=ProjectMemberResponse,
)
def add_project_member(
    project_id: str,
    payload: ProjectMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = add_member_to_project(
            db,
            project_id,
            payload.user_id,
            current_user,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")

    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if result == "USER_NOT_FOUND":
        raise HTTPException(status_code=404, detail="User not found")

    if result == "ALREADY_MEMBER":
        raise HTTPException(status_code=400, detail="User already member")

    return result

@router.delete("/{project_id}/members/{user_id}", status_code=204)
def delete_project_member(
    project_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result = remove_member_from_project(
            db,
            project_id,
            user_id,
            current_user,
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")

    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if result is False:
        raise HTTPException(status_code=404, detail="Membership not found")

    return None

