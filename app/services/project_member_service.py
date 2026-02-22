from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from datetime import datetime
import uuid
from app.services.access_service import AccessService


class ProjectMemberService:
    @classmethod
    async def add_member_to_project_service(
        cls,
        db: AsyncSession,
        project_id: str,
        user_id: str,
        current_user: User,
    ) -> Union[ProjectMember, str, None]:
        # Only owner can add members
        access = await AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Only owner can add members")

        # Check user exists
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return "USER_NOT_FOUND"

        # Prevent duplicate membership
        result = await db.execute(
            select(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            return "ALREADY_MEMBER"

        membership = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            joined_at=datetime.utcnow(),
        )

        db.add(membership)
        await db.commit()
        await db.refresh(membership)

        return membership

    @classmethod
    async def list_project_members_service(
        cls,
        db: AsyncSession,
        project_id: str,
        current_user: User,
    ) -> List[ProjectMember]:
        # Check if user has access to view members
        access = await AccessService.get_project_with_access(db, project_id, current_user)
        
        if access is None:
            return []
            
        if access is False:
            raise PermissionError("Not allowed to view members")

        result = await db.execute(
            select(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .filter(ProjectMember.project_id == project_id)
        )
        return result.scalars().all()

    @classmethod
    async def remove_member_from_project_service(
        cls,
        db: AsyncSession,
        project_id: str,
        user_id: str,
        current_user: User,
    ) -> bool:
        # Only owner can remove members
        access = await AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Only owner can remove members")

        result = await db.execute(
            select(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        membership = result.scalar_one_or_none()

        if not membership:
            return False

        await db.delete(membership)
        await db.commit()

        return True
