from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.access_service import AccessService


class ProjectService:
    @classmethod
    async def create_project_service(
        cls,
        db: AsyncSession,
        project_in: ProjectCreate,
        current_user: User,
    ) -> Project:
        project = Project(
            name=project_in.name,
            description=project_in.description,
            owner_id=current_user.id,
        )

        db.add(project)
        await db.commit()
        await db.refresh(project)

        return project

    @classmethod
    async def get_user_projects_service(cls, db: AsyncSession, current_user: User) -> List[Project]:
        result = await db.execute(
            select(Project)
            .outerjoin(
                ProjectMember,
                Project.id == ProjectMember.project_id,
            )
            .filter(
                or_(
                    Project.owner_id == current_user.id,
                    ProjectMember.user_id == current_user.id,
                )
            )
            .distinct()
        )
        return result.scalars().all()

    @classmethod
    async def get_project_by_id_service(
        cls,
        db: AsyncSession,
        project_id: str,
        current_user: User,
    ) -> Union[Project, None]:
        access = await AccessService.get_project_with_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Not allowed to access this project")
            
        return access

    @classmethod
    async def update_project_service(
        cls,
        db: AsyncSession,
        project_id: str,
        project_in: ProjectUpdate,
        current_user: User,
    ) -> Union[Project, None]:
        access = await AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Not allowed to update this project")

        if project_in.name is not None:
            access.name = project_in.name

        if project_in.description is not None:
            access.description = project_in.description

        await db.commit()
        await db.refresh(access)

        return access

    @classmethod
    async def delete_project_service(
        cls,
        db: AsyncSession,
        project_id: str,
        current_user: User,
    ) -> bool:
        access = await AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return False
            
        if access is False:
            raise PermissionError("Not allowed to delete this project")

        await db.delete(access)
        await db.commit()

        return True
