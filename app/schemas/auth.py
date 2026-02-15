from pydantic import BaseModel, EmailStr
from typing import Literal


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: Literal["MANAGER", "MEMBER"]


class SignupResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
