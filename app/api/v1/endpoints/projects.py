from fastapi import APIRouter, status, Depends, HTTPException
from typing import List

from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.project_member import (
    ProjectMemberAdd,
    ProjectMemberResponse,
    ProjectMemberListResponse,
)

from app.services.project_member_service import ProjectMemberService
from app.services.project_service import ProjectService
from app.core.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectResponse,
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await ProjectService.create_project_service(db, payload, current_user)
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectService.get_user_projects_service(db, current_user)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await ProjectService.get_project_by_id_service(db, project_id, current_user)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = await ProjectService.update_project_service(
        db, project_id, payload, current_user
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await ProjectService.delete_project_service(
        db, project_id, current_user
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return None


@router.get("/{project_id}/members", response_model=List[ProjectMemberListResponse])
async def get_project_members(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await ProjectMemberService.list_project_members_service(db, project_id, current_user)


@router.post(
    "/{project_id}/members",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectMemberResponse,
)
async def add_project_member(
    project_id: str,
    payload: ProjectMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await ProjectMemberService.add_member_to_project_service(
        db,
        project_id,
        payload.user_id,
        current_user,
    )

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if result == "USER_NOT_FOUND":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if result == "ALREADY_MEMBER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already member")
        
    return result


@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_member(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await ProjectMemberService.remove_member_from_project_service(
        db,
        project_id,
        user_id,
        current_user,
    )

    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if result is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    return None

