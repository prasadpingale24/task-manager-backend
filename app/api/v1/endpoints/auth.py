from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


# Temporary request models (real ones will move to schemas/)
class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str
    role: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest):
    return {
        "message": "Signup placeholder - not implemented",
        "user": {
            "id": "temp-id-123",
            "email": payload.email,
            "full_name": payload.full_name,
            "role": payload.role
        }
    }


@router.post("/login")
def login(payload: LoginRequest):
    return {
        "access_token": "fake-jwt-token",
        "token_type": "bearer"
    }
