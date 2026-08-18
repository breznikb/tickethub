from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from tickethub.core.db import get_db
from tickethub.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from tickethub.models.user import User
from tickethub.schemas.auth import Token, UserCreate, UserPublic
from tickethub.core.config import RATE_LIMIT_LOGIN
from tickethub.core.rate_limit import limiter


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    normalized_username = payload.username.strip().lower()

    existing = await db.scalar(
        select(User).where(User.username == normalized_username)
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Username is already registered",
        )

    user = User(
        username=normalized_username,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username is already registered",
        )

    await db.refresh(user)
    return user


@router.post("/token", response_model=Token)
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    normalized_username = form.username.strip().lower()

    user = await db.scalar(
        select(User).where(User.username == normalized_username)
    )

    if user is None or not verify_password(
        form.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(
        access_token=create_access_token(user.id),
        token_type="bearer",
    )
