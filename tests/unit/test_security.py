import pytest
from app.core.security import hash_password, verify_password, create_access_token
from jose import jwt
from app.core.config import settings

def test_password_hashing():
    password = "secret_password"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_access_token_creation():
    data = {"sub": "test@example.com", "role": "MANAGER"}
    token = create_access_token(data)
    assert isinstance(token, str)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == data["sub"]
    assert payload["role"] == data["role"]
    assert "exp" in payload
