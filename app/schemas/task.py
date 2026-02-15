from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class TaskCreate(BaseModel):
    project_id: str
    title: str
    description: str
    status: Literal["ACTIVE", "PENDING", "COMPLETE"]


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Literal["ACTIVE", "PENDING", "COMPLETE"]] = None


class TaskResponse(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
