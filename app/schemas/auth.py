from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
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


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str


class MessageResponse(BaseModel):
    message: str
