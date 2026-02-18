from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User


def check_project_access(
    db: Session,
    project_id: str,
    current_user: User,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return None

    # Owner has access
    if project.owner_id == current_user.id:
        return project

    # Check membership
    membership = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id,
        )
        .first()
    )

    if membership:
        return project

    return False
