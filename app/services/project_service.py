from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.models.user import User


def create_project_service(
    db: Session,
    project_in: ProjectCreate,
    current_user: User,
):
    project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def get_user_projects(
    db: Session,
    current_user: User,
):
    return (
        db.query(Project)
        .filter(Project.owner_id == current_user.id)
        .all()
    )


def get_project_by_id(
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

    if project.owner_id != current_user.id:
        raise PermissionError("Not allowed to access this project")

    return project
