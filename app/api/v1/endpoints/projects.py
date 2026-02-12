from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import List

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: str


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate):
    return {
        "id": "proj-123",
        "name": payload.name,
        "description": payload.description,
        "created_at": "2026-02-13T12:00:00Z"
    }


@router.get("/", response_model=List[dict])
def list_projects():
    return [
        {
            "id": "proj-123",
            "name": "Internal Platform",
            "description": "Placeholder project",
            "created_at": "2026-02-13T12:00:00Z"
        }
    ]


@router.get("/{project_id}")
def get_project(project_id: str):
    return {
        "id": project_id,
        "name": "Internal Platform",
        "description": "Placeholder project",
        "created_at": "2026-02-13T12:00:00Z"
    }
