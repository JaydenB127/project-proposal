import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import APIResponse, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


@router.post("/register", response_model=APIResponse)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.username == payload.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=_hash_password(payload.password),
    )
    db.add(user)
    await db.flush()
    return APIResponse(success=True, data=UserOut.model_validate(user, from_attributes=True).model_dump())


@router.get("/me", response_model=APIResponse)
async def get_me(db: AsyncSession = Depends(get_db)):
    # Minimal stub — full auth in Phase 2
    return APIResponse(success=True, data={"message": "Auth endpoint active"})
