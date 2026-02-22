from typing import List, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.models.task import Task
from app.models.user import User
from app.models.user_task_status import UserTaskStatus
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskUpdate, TaskOwnerResponse, MemberTaskStatus
from app.services.access_service import AccessService
import uuid


class TaskService:
    @classmethod
    async def create_task_service(cls, db: AsyncSession, task_in: TaskCreate, current_user: User) -> Union[Task, None]:
        # Check project exists
        access = await AccessService.get_project_with_access(db, task_in.project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Not allowed to create task in this project")

        task = Task(
            id=str(uuid.uuid4()),
            project_id=task_in.project_id,
            title=task_in.title,
            description=task_in.description,
            status=task_in.status,
            created_by_id=current_user.id
        )
        
        db.add(task)
        await db.commit()
        await db.refresh(task)
        
        return task

    @classmethod
    async def get_project_tasks_service(cls, db: AsyncSession, project_id: str, current_user: User) -> List[Union[TaskOwnerResponse, Task]]:
        access = await AccessService.get_project_with_access(db, project_id, current_user)
        
        if access is None:
            return []
            
        if access is False:
            raise PermissionError("Not allowed to access this project")

        is_owner = access.owner_id == current_user.id
        
        result = await db.execute(select(Task).filter(Task.project_id == project_id))
        tasks = result.scalars().all()
        
        if is_owner:
            owner_tasks = [t for t in tasks if t.created_by_id == current_user.id]
            
            response_tasks = []
            for t in owner_tasks:
                result = await db.execute(
                    select(UserTaskStatus)
                    .options(joinedload(UserTaskStatus.user))
                    .filter(UserTaskStatus.task_id == t.id)
                )
                member_statuses = result.scalars().all()
                
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
            member_visible_tasks = [
                t for t in tasks if (t.created_by_id == access.owner_id) or (t.created_by_id == current_user.id)
            ]
            
            for t in member_visible_tasks:
                if t.created_by_id == access.owner_id:
                    result = await db.execute(
                        select(UserTaskStatus).filter(
                            UserTaskStatus.task_id == t.id,
                            UserTaskStatus.user_id == current_user.id
                        )
                    )
                    user_status = result.scalar_one_or_none()
                    if user_status:
                        t.status = user_status.status
            return member_visible_tasks

    @classmethod
    async def get_task_by_id_service(cls, db: AsyncSession, task_id: str, current_user: User) -> Union[TaskOwnerResponse, Task, None]:
        task = await AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return None
            
        if task is False:
            raise PermissionError("Not allowed to access this task")

        result = await db.execute(select(Project).filter(Project.id == task.project_id))
        project = result.scalar_one_or_none()
        
        if project and project.owner_id == current_user.id and task.created_by_id == project.owner_id:
            result = await db.execute(
                select(UserTaskStatus)
                .options(joinedload(UserTaskStatus.user))
                .filter(UserTaskStatus.task_id == task_id)
            )
            member_statuses = result.scalars().all()
            
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

        if project and task.created_by_id == project.owner_id and project.owner_id != current_user.id:
            result = await db.execute(
                select(UserTaskStatus).filter(
                    UserTaskStatus.task_id == task.id,
                    UserTaskStatus.user_id == current_user.id
                )
            )
            user_status = result.scalar_one_or_none()
            if user_status:
                task.status = user_status.status

        return task

    @classmethod
    async def update_task_service(cls, db: AsyncSession, task_id: str, task_in: TaskUpdate, current_user: User) -> Union[Task, None]:
        task = await AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return None
            
        if task is False:
            raise PermissionError("Not allowed to update this task")

        result = await db.execute(select(Project).filter(Project.id == task.project_id))
        project = result.scalar_one_or_none()
        
        if task.created_by_id == project.owner_id:
            if current_user.id == project.owner_id:
                if task_in.title is not None:
                    task.title = task_in.title
                if task_in.description is not None:
                    task.description = task_in.description
                if task_in.status is not None:
                    task.status = task_in.status
            else:
                if task_in.status is not None:
                    result = await db.execute(
                        select(UserTaskStatus).filter(
                            UserTaskStatus.task_id == task_id,
                            UserTaskStatus.user_id == current_user.id
                        )
                    )
                    user_status = result.scalar_one_or_none()
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
                    task.status = task_in.status
        else:
            if task_in.title is not None:
                task.title = task_in.title
            if task_in.description is not None:
                task.description = task_in.description
            if task_in.status is not None:
                task.status = task_in.status

        await db.commit()
        await db.refresh(task)
        
        return task

    @classmethod
    async def delete_task_service(cls, db: AsyncSession, task_id: str, current_user: User) -> bool:
        task = await AccessService.get_task_with_access(db, task_id, current_user)
        
        if task is None:
            return False
            
        if task is False:
            raise PermissionError("Not allowed to delete this task")

        if task.created_by_id != current_user.id:
            raise PermissionError("Only the creator of a task can delete it")

        await db.delete(task)
        await db.commit()

        return True
