from fastapi import APIRouter, status, Depends
from typing import List
from datetime import datetime

from app.schemas.project import ProjectCreate, ProjectResponse
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
def create_project(payload: ProjectCreate, current_user: User = Depends(get_current_user)):
    return {
        "id": "proj-123",
        "name": payload.name,
        "description": payload.description,
        "created_at": datetime.utcnow()
    }


@router.get("/", response_model=List[ProjectResponse])
def list_projects(current_user: User = Depends(get_current_user)):
    return [
        {
            "id": "proj-123",
            "name": "Internal Platform",
            "description": "Placeholder project",
            "created_at": datetime.utcnow()
        }
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    return {
        "id": project_id,
        "name": "Internal Platform",
        "description": "Placeholder project",
        "created_at": datetime.utcnow()
    }
