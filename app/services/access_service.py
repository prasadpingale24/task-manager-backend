from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User


class AccessService:
    @classmethod
    async def get_project_with_access(cls, db: AsyncSession, project_id: str, current_user: User) -> Union[Project, bool, None]:
        """
        Returns:
        - Project: if access granted (Owner or Member)
        - False: if project exists but access denied
        - None: if project not found
        """
        result = await db.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
            
        # Check if the user is the owner
        if project.owner_id == current_user.id:
            return project

        # Check if the user is a member
        result = await db.execute(
            select(ProjectMember).filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id
            )
        )
        membership = result.scalar_one_or_none()
        if membership:
            return project

        return False

    @classmethod
    async def get_project_owner_access(cls, db: AsyncSession, project_id: str, current_user: User) -> Union[Project, bool, None]:
        """
        Returns:
        - Project: if user is the Owner
        - False: if project exists but user is not Owner
        - None: if project not found
        """
        result = await db.execute(select(Project).filter(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
            
        if project.owner_id == current_user.id:
            return project
            
        return False

    @classmethod
    async def get_task_with_access(cls, db: AsyncSession, task_id: str, current_user: User) -> Union[Task, bool, None]:
        """
        Returns:
        - Task: if access granted
        - False: if task exists but access denied
        - None: if task not found
        """
        result = await db.execute(select(Task).filter(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None
            
        result = await db.execute(select(Project).filter(Project.id == task.project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None

        # Rule 1: Creator always has access
        if task.created_by_id == current_user.id:
            return task

        # Rule 2: If task was created by project owner (Common Task), all members have access
        if task.created_by_id == project.owner_id:
            result = await db.execute(
                select(ProjectMember).filter(
                    ProjectMember.project_id == project.id,
                    ProjectMember.user_id == current_user.id
                )
            )
            membership = result.scalar_one_or_none()
            if membership:
                return task

        return False

    # Aliases for backward compatibility
    check_project_access = get_project_with_access
    check_project_task_access = get_project_with_access
    check_task_access = get_task_with_access
