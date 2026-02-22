from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import SignupRequest
from app.core.security import hash_password, verify_password, create_access_token


async def register_user_service(db: AsyncSession, payload: SignupRequest):
    result = await db.execute(select(User).filter(User.email == payload.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return "EMAIL_EXISTS"

    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(payload.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def login_user_service(db: AsyncSession, email: str, password: str):
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalar_one_or_none()

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
