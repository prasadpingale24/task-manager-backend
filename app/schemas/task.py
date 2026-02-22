from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal, List
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
    created_by_id: str
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberTaskStatus(BaseModel):
    user_id: str
    full_name: str
    status: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskOwnerResponse(TaskResponse):
    member_statuses: List[MemberTaskStatus] = []
