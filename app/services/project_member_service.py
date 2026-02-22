from typing import List, Union
from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from datetime import datetime
import uuid
from app.services.access_service import AccessService


class ProjectMemberService:
    @classmethod
    def add_member_to_project_service(
        cls,
        db: Session,
        project_id: str,
        user_id: str,
        current_user: User,
    ) -> Union[ProjectMember, str, None]:
        # Only owner can add members
        access = AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Only owner can add members")

        # No longer preventing owner from being member
        # if user_id == access.owner_id:
        #     return "OWNER_CANNOT_BE_MEMBER"

        # Check user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return "USER_NOT_FOUND"

        # Prevent duplicate membership
        existing = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

        if existing:
            return "ALREADY_MEMBER"

        membership = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=user_id,
            joined_at=datetime.utcnow(),
        )

        db.add(membership)
        db.commit()
        db.refresh(membership)

        return membership

    @classmethod
    def list_project_members_service(
        cls,
        db: Session,
        project_id: str,
        current_user: User,
    ) -> List[ProjectMember]:
        # Check if user has access to view members
        access = AccessService.get_project_with_access(db, project_id, current_user)
        
        if access is None:
            return []
            
        if access is False:
            raise PermissionError("Not allowed to view members")

        return (
            db.query(ProjectMember)
            .options(joinedload(ProjectMember.user))
            .filter(ProjectMember.project_id == project_id)
            .all()
        )

    @classmethod
    def remove_member_from_project_service(
        cls,
        db: Session,
        project_id: str,
        user_id: str,
        current_user: User,
    ) -> bool:
        # Only owner can remove members
        access = AccessService.get_project_owner_access(db, project_id, current_user)
        
        if access is None:
            return None
            
        if access is False:
            raise PermissionError("Only owner can remove members")

        membership = (
            db.query(ProjectMember)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .first()
        )

        if not membership:
            return False

        db.delete(membership)
        db.commit()

        return True
