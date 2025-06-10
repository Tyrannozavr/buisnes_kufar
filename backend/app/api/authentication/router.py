from typing import Annotated

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.dependencies import AuthServiceDep
from app.api.authentication.schemas.user import User, Token, UserCreateStep1, UserCreateStep2
from app.api.authentication.services.auth_service import AuthService
from app.core.config import settings
from app.core.security import get_current_user_id_from_token
from app.db.base import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
async def register_step1(
        data: UserCreateStep1,
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    await auth_service.register_step1(data)
    return {"message": "Registration email sent"}


@router.post("/register/step2", status_code=status.HTTP_201_CREATED)
async def register_step2(
        data: UserCreateStep2,
        response: Response,
        db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.register_step2(data)

    # Create access token
    access_token = await auth_service.create_access_token_cookie(user.id)

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,  # True in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"message": "Registration completed successfully"}


@router.get("/verify-token/{token}")
async def verify_token(
        token: str,
        auth_service: AuthServiceDep
) -> dict:
    is_valid = await auth_service.verify_token(token)
    return {"is_valid": is_valid}


@router.post("/login", response_model=Token)
async def login(
        response: Response,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AuthServiceDep
) -> Token:
    token = await auth_service.login(form_data.username, form_data.password)

    # Устанавливаем cookie с токеном
    response.set_cookie(
        key="access_token",
        value=token.access_token,
        httponly=True,
        secure=True,  # для HTTPS
        samesite="lax",
        max_age=3600  # 1 час
    )

    return token


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_current_user(
        auth_service: AuthServiceDep,
        access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_id = get_current_user_id_from_token(access_token)
    user = await auth_service.get_current_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
