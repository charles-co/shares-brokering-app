from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import or_

from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    pwd_context,
)
from app.core.config import settings
from app.db.database import get_session
from app.models import User
from app.schemas.token import Token
from app.schemas.user import UserModelSchema, UserRegistrationSchema

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/users/me/", response_model=UserModelSchema, status_code=status.HTTP_200_OK
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return UserModelSchema.from_orm(current_user)


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def user_registration(
    user: UserRegistrationSchema, db: AsyncSession = Depends(get_session)
):
    try:
        statement = select(User).where(
            or_(User.email == user.email, User.username == user.username)
        )
        result = await db.execute(statement)
        user = result.one()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Username or email already exists",
        )
    except NoResultFound:
        data = user.dict()
        data.update({"hashed_password": pwd_context.hash(data["password"])})
        data.pop("password", None)
        user: User = User(**data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        access_token = create_access_token(data={"user_id": user.id})
        return {"access_token": access_token}
