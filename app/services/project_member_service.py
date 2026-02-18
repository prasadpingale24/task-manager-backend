from sqlalchemy.orm import Session, joinedload
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from datetime import datetime
import uuid


def add_member_to_project(
    db: Session,
    project_id: str,
    user_id: str,
    current_user: User,
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return None

    # Only owner can add
    if project.owner_id != current_user.id:
        raise PermissionError("Only owner can add members")

    # Prevent adding owner
    if user_id == project.owner_id:
        raise ValueError("Owner is already part of the project")

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


def list_project_members(
    db: Session,
    project_id: str,
):
    return (
        db.query(ProjectMember)
        .options(joinedload(ProjectMember.user))
        .filter(ProjectMember.project_id == project_id)
        .all()
    )


def remove_member_from_project(
    db: Session,
    project_id: str,
    user_id: str,
    current_user: User,
):
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        return None

    # Only owner can remove
    if project.owner_id != current_user.id:
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
