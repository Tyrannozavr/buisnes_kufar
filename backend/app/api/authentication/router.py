from typing import Annotated
from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.authentication.dependencies import AuthServiceDep
from app.api.authentication.schemas.user import User, Token, RegistrationToken, UserCreateStep1, UserCreateStep2
from app.core.security import get_current_user_id_from_token
from uuid import UUID

router = APIRouter()


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
async def register_step1(
        user_data: UserCreateStep1,
        auth_service: AuthServiceDep
) -> None:
    await auth_service.register_step1(user_data)


@router.post("/register/step2", response_model=Token)
async def register_step2(
        data: UserCreateStep2,
        response: Response,
        auth_service: AuthServiceDep
) -> Token:
    user, token = await auth_service.register_step2(data)
    
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
