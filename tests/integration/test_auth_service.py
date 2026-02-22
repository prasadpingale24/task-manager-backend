import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import register_user_service, login_user_service
from app.schemas.auth import SignupRequest
from app.models.user import User
from sqlalchemy import select

@pytest.mark.asyncio
async def test_register_user_service(db: AsyncSession):
    payload = SignupRequest(
        email="test_service@example.com",
        password="testpassword123",
        full_name="Service Tester",
        role="MANAGER"
    )
    
    # Test registration
    user = await register_user_service(db, payload)
    assert isinstance(user, User)
    assert user.email == payload.email
    assert user.full_name == payload.full_name
    
    # Test duplicate email
    result = await register_user_service(db, payload)
    assert result == "EMAIL_EXISTS"

@pytest.mark.asyncio
async def test_login_user_service(db: AsyncSession):
    email = "login_test@example.com"
    password = "testpassword123"
    
    # Register first
    payload = SignupRequest(
        email=email,
        password=password,
        full_name="Login Tester",
        role="MEMBER"
    )
    await register_user_service(db, payload)
    
    # Test successful login
    login_result = await login_user_service(db, email, password)
    assert login_result is not None
    assert "access_token" in login_result
    assert login_result["token_type"] == "bearer"
    
    # Test wrong password
    wrong_password_result = await login_user_service(db, email, "wrongpassword")
    assert wrong_password_result is None
    
    # Test non-existent user
    non_existent_result = await login_user_service(db, "none@example.com", password)
    assert non_existent_result is None
