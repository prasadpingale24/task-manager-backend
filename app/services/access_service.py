from typing import Union
from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.task import Task
from app.models.user import User


class AccessService:
    @classmethod
    def get_project_with_access(cls, db: Session, project_id: str, current_user: User) -> Union[Project, bool, None]:
        """
        Returns:
        - Project: if access granted (Owner or Member)
        - False: if project exists but access denied
        - None: if project not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
            
        # Check if the user is the owner
        if project.owner_id == current_user.id:
            return project

        # Check if the user is a member
        membership = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()
        if membership:
            return project

        return False

    @classmethod
    def get_project_owner_access(cls, db: Session, project_id: str, current_user: User) -> Union[Project, bool, None]:
        """
        Returns:
        - Project: if user is the Owner
        - False: if project exists but user is not Owner
        - None: if project not found
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
            
        if project.owner_id == current_user.id:
            return project
            
        return False

    @classmethod
    def get_task_with_access(cls, db: Session, task_id: str, current_user: User) -> Union[Task, bool, None]:
        """
        Returns:
        - Task: if access granted
        - False: if task exists but access denied
        - None: if task not found
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
            
        project = db.query(Project).filter(Project.id == task.project_id).first()
        if not project:
            return None

        # Rule 1: Creator always has access
        if task.created_by_id == current_user.id:
            return task

        # Rule 2: If task was created by project owner (Common Task), all members have access
        if task.created_by_id == project.owner_id:
            membership = db.query(ProjectMember).filter(
                ProjectMember.project_id == project.id,
                ProjectMember.user_id == current_user.id
            ).first()
            if membership:
                return task

        return False

    # Aliases for backward compatibility
    check_project_access = get_project_with_access
    check_project_task_access = get_project_with_access # Fixed the name mismatch from task_service.py
    check_task_access = get_task_with_access
