import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.project_service import ProjectService
from app.services.auth_service import register_user_service
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.auth import SignupRequest
from app.models.user import User
from app.models.project import Project

@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    payload = SignupRequest(
        email="owner@example.com",
        password="testpassword123",
        full_name="Project Owner",
        role="MANAGER"
    )
    return await register_user_service(db, payload)

@pytest_asyncio.fixture
async def other_user(db: AsyncSession) -> User:
    payload = SignupRequest(
        email="other@example.com",
        password="testpassword123",
        full_name="Other User",
        role="MEMBER"
    )
    return await register_user_service(db, payload)

@pytest.mark.asyncio
async def test_create_project_service(db: AsyncSession, test_user: User):
    project_in = ProjectCreate(name="Test Project", description="Test Description")
    project = await ProjectService.create_project_service(db, project_in, test_user)
    
    assert isinstance(project, Project)
    assert project.name == "Test Project"
    assert project.owner_id == test_user.id

@pytest.mark.asyncio
async def test_get_user_projects_service(db: AsyncSession, test_user: User):
    # Create two projects
    await ProjectService.create_project_service(
        db, ProjectCreate(name="P1"), test_user
    )
    await ProjectService.create_project_service(
        db, ProjectCreate(name="P2"), test_user
    )
    
    projects = await ProjectService.get_user_projects_service(db, test_user)
    assert len(projects) == 2

@pytest.mark.asyncio
async def test_project_access_permissions(db: AsyncSession, test_user: User, other_user: User):
    # Owner creates project
    project = await ProjectService.create_project_service(
        db, ProjectCreate(name="Secure Project"), test_user
    )
    
    # Owner should have access
    retrieved = await ProjectService.get_project_by_id_service(db, project.id, test_user)
    assert retrieved.id == project.id
    
    # Other user should NOT have access (None if not exists/found, but here it exists)
    # Actually, AccessService.get_project_with_access returns False if found but no access
    with pytest.raises(PermissionError) as exc:
        await ProjectService.get_project_by_id_service(db, project.id, other_user)
    assert "Not allowed to access" in str(exc.value)

@pytest.mark.asyncio
async def test_update_project_service(db: AsyncSession, test_user: User):
    project = await ProjectService.create_project_service(
        db, ProjectCreate(name="Old Name"), test_user
    )
    
    update_in = ProjectUpdate(name="New Name")
    updated = await ProjectService.update_project_service(db, project.id, update_in, test_user)
    
    assert updated.name == "New Name"

@pytest.mark.asyncio
async def test_delete_project_service(db: AsyncSession, test_user: User):
    project = await ProjectService.create_project_service(
        db, ProjectCreate(name="Delete Me"), test_user
    )
    
    success = await ProjectService.delete_project_service(db, project.id, test_user)
    assert success is True
    
    # Verify it's gone
    retrieved = await ProjectService.get_project_by_id_service(db, project.id, test_user)
    assert retrieved is None
