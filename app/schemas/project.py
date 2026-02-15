from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    description: str


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
