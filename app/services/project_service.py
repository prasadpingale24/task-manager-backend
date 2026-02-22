from typing import List, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.services.access_service import AccessService


class ProjectService:
    @classmethod
    def create_project_service(
        cls,
        db: Session,
        project_in: ProjectCreate,
        current_user: User,
    ) -> Project:
        project = Project(
            name=project_in.name,
            description=project_in.description,
            owner_id=current_user.id,
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @classmethod
    def get_user_projects_service(cls, db: Session, current_user: User) -> List[Project]:
        return (
            db.query(Project)
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
            .all()
        )

    @classmethod
    def get_project_by_id_service(
        cls,
        db: Session,
        project_id: str,
        current_user: User,
    ) -> Union[Project, None]:
        access = AccessService.get_project_with_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Not allowed to access this project")
            
        return access

    @classmethod
    def update_project_service(
        cls,
        db: Session,
        project_id: str,
        project_in: ProjectUpdate,
        current_user: User,
    ) -> Union[Project, None]:
        # Only owner can update project details (usually)
        # Let's check if we want to allow members to update. 
        # Typically only owner or admin. Let's use get_project_owner_access for update.
        access = AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Not allowed to update this project")

        if project_in.name is not None:
            access.name = project_in.name

        if project_in.description is not None:
            access.description = project_in.description

        db.commit()
        db.refresh(access)

        return access

    @classmethod
    def delete_project_service(
        cls,
        db: Session,
        project_id: str,
        current_user: User,
    ) -> bool:
        access = AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return False
            
        if access is False:
            raise PermissionError("Not allowed to delete this project")

        db.delete(access)
        db.commit()

        return True
