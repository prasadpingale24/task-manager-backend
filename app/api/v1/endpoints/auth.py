from fastapi import APIRouter, status
from app.schemas.auth import (
    SignupRequest,
    SignupResponse,
    LoginRequest,
    TokenResponse
)

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=SignupResponse)
def signup(payload: SignupRequest):
    return {
        "id": "temp-id-123",
        "email": payload.email,
        "full_name": payload.full_name,
        "role": payload.role
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return {
        "access_token": "fake-jwt-token",
        "token_type": "bearer"
    }
