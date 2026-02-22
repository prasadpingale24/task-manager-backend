from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse,
    UserResponse,
    MessageResponse
)
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.auth_service import login_user_service, register_user_service

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
async def signup(payload: SignupRequest, db: AsyncSession = Depends(get_db)):

    result = await register_user_service(db, payload)

    if result == "EMAIL_EXISTS":
        raise HTTPException(status_code=400, detail="Email already registered")

    return SignupResponse(
        id=result.id,
        email=result.email,
        full_name=result.full_name,
        role=result.role
    )

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await login_user_service(db, payload.email, payload.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile.
    """
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.
    """
    # For stateless JWT, we primarily handle this on the frontend by deleting the token.
    # This endpoint provides a semantic way for the frontend to acknowledge logout.
    return {"message": "Successfully logged out"}

