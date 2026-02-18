from pydantic import BaseModel
from datetime import datetime

class ProjectMemberUserInfo(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True


class ProjectMemberListResponse(BaseModel):
    id: str
    project_id: str
    joined_at: datetime
    user: ProjectMemberUserInfo

    class Config:
        from_attributes = True


class ProjectMemberAdd(BaseModel):
    user_id: str


class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    joined_at: datetime

    class Config:
        from_attributes = True
