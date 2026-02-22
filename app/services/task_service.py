from typing import List, Union
from datetime import datetime
import uuid

from sqlalchemy.orm import Session, joinedload
from app.models.task import Task
from app.models.user import User
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user_task_status import UserTaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskOwnerResponse, MemberTaskStatus
from app.services.access_service import AccessService


class TaskService:
    @classmethod
    def create_task_service(cls, db: Session, task_in: TaskCreate, current_user: User) -> Union[Task, None]:
        access = AccessService.get_project_with_access(db, task_in.project_id, current_user)

        if access is None:
            return None

        if access is False:
            raise PermissionError("Not allowed to create task in this project")

        task = Task(
            id=str(uuid.uuid4()),
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            project_id=task_in.project_id,
            created_by_id=current_user.id,
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @classmethod
    def get_task_by_id_service(cls, db: Session, task_id: str, current_user: User) -> Union[Task, TaskOwnerResponse, None]:
        task = AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return None
            
        if task is False:
            raise PermissionError("Not allowed to access this task")
            
        project = db.query(Project).filter(Project.id == task.project_id).first()
        is_owner = project.owner_id == current_user.id
        
        if is_owner and task.created_by_id == current_user.id:
            # If viewer is owner and it's a common task (created by them), include member statuses
            member_statuses = (
                db.query(UserTaskStatus)
                .options(joinedload(UserTaskStatus.user))
                .filter(UserTaskStatus.task_id == task_id)
                .all()
            )
            
            owner_task = TaskOwnerResponse.model_validate(task)
            owner_task.member_statuses = [
                MemberTaskStatus(
                    user_id=s.user_id,
                    full_name=s.user.full_name,
                    status=s.status,
                    updated_at=s.updated_at
                ) for s in member_statuses
            ]
            return owner_task

        # For members, inject their status if it's a common task
        if task.created_by_id == project.owner_id:
            user_status = db.query(UserTaskStatus).filter(
                UserTaskStatus.task_id == task_id,
                UserTaskStatus.user_id == current_user.id
            ).first()
            if user_status:
                task.status = user_status.status

        return task

    @classmethod
    def get_project_tasks_service(cls, db: Session, project_id: str, current_user: User) -> List[Union[Task, TaskOwnerResponse]]:
        access = AccessService.get_project_with_access(db, project_id, current_user)

        if access is None:
            return []

        if access is False:
            raise PermissionError("Not allowed to view tasks in this project")

        # Get all tasks for the project that are either common (created by owner) or created by the current user
        is_owner = access.owner_id == current_user.id
        
        query = db.query(Task).filter(Task.project_id == project_id)
        
        if is_owner:
            # Owner sees all their created tasks (common) and their own private tasks
            tasks = query.filter(Task.created_by_id == current_user.id).all()
            
            response_tasks = []
            for t in tasks:
                # If it's a common task, include member statuses
                # A task is common if created_by_id == project.owner_id (which is current_user in this block)
                member_statuses = (
                    db.query(UserTaskStatus)
                    .options(joinedload(UserTaskStatus.user))
                    .filter(UserTaskStatus.task_id == t.id)
                    .all()
                )
                
                owner_task = TaskOwnerResponse.model_validate(t)
                owner_task.member_statuses = [
                    MemberTaskStatus(
                        user_id=s.user_id,
                        full_name=s.user.full_name,
                        status=s.status,
                        updated_at=s.updated_at
                    ) for s in member_statuses
                ]
                response_tasks.append(owner_task)
            return response_tasks
        else:
            # Member sees common tasks (created by owner) and their own private tasks
            tasks = query.filter(
                (Task.created_by_id == access.owner_id) | 
                (Task.created_by_id == current_user.id)
            ).all()
            
            for t in tasks:
                # If it's a common task, we should use the user's specific status
                if t.created_by_id == access.owner_id:
                    user_status = db.query(UserTaskStatus).filter(
                        UserTaskStatus.task_id == t.id,
                        UserTaskStatus.user_id == current_user.id
                    ).first()
                    if user_status:
                        t.status = user_status.status
                    else:
                        # Default is the one in Task model, but maybe we should ensure UserTaskStatus exists?
                        # For now use the task's default status
                        pass
            return tasks

    @classmethod
    def update_task_service(cls, db: Session, task_id: str, task_in: TaskUpdate, current_user: User) -> Union[Task, None]:
        task = AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return None
            
        if task is False:
            raise PermissionError("Not allowed to update this task")

        project = db.query(Project).filter(Project.id == task.project_id).first()
        is_owner = project.owner_id == current_user.id
        is_creator = task.created_by_id == current_user.id

        # Rules:
        # 1. Owner can update metadata (title, description) of any task they created (Common or Private).
        # 2. Creator (if member) can update everything of their private task.
        # 3. Member can ONLY update their status for common tasks.

        if is_creator:
            # Full control for creator
            if task_in.title is not None:
                task.title = task_in.title
            if task_in.description is not None:
                task.description = task_in.description
            if task_in.status is not None:
                task.status = task_in.status
            
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)
            return task
        else:
            # User is Not the creator. They must be a member and it must be a common task.
            if task.created_by_id == project.owner_id:
                # Update individual status in UserTaskStatus
                if task_in.status is not None:
                    user_status = db.query(UserTaskStatus).filter(
                        UserTaskStatus.task_id == task_id,
                        UserTaskStatus.user_id == current_user.id
                    ).first()
                    
                    if not user_status:
                        user_status = UserTaskStatus(
                            id=str(uuid.uuid4()),
                            task_id=task_id,
                            user_id=current_user.id,
                            status=task_in.status
                        )
                        db.add(user_status)
                    else:
                        user_status.status = task_in.status
                    
                    db.commit()
                    # We return the task but with the user's status injected
                    task.status = task_in.status
                    return task
                else:
                    # Member tried to update something they can't (title/desc)
                    raise PermissionError("Members can only update the status of common tasks")
            else:
                # This should technically be caught by AccessService but being safe
                raise PermissionError("Not allowed to update this private task")

    @classmethod
    def delete_task_service(cls, db: Session, task_id: str, current_user: User) -> bool:
        task = AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return False
            
        if task is False:
            raise PermissionError("Not allowed to delete this task")

        # Restrict deletion to the creator
        if task.created_by_id != current_user.id:
            raise PermissionError("Only the creator of a task can delete it")

        db.delete(task)
        db.commit()

        return True
