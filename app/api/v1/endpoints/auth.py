from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse
)
from app.core.dependencies import get_db
from app.services.auth_service import login_user_service, register_user_service

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    result = register_user_service(db, payload)

    if result == "EMAIL_EXISTS":
        raise HTTPException(status_code=400, detail="Email already registered")

    return SignupResponse(
        id=result.id,
        email=result.email,
        full_name=result.full_name,
        role=result.role
    )

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    result = login_user_service(db, payload.email, payload.password)

    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result

