from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import SignupRequest
from app.core.security import hash_password, verify_password, create_access_token


def register_user_service(db: Session, payload: SignupRequest):
    existing_user = db.query(User).filter(User.email == payload.email).first()

    if existing_user:
        return "EMAIL_EXISTS"

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user_service(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    access_token = create_access_token(
        data={
            "sub": user.id,
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
