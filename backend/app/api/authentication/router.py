from typing import Optional

from fastapi import APIRouter, Response, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer

from app.api.authentication.dependencies import AuthServiceDep, token_data_dep
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import User, UserCreateStep1, UserCreateStep2, Token, VerifyTokenResponse
from app.api.authentication.services.auth_service import AuthService
from app.api.company.dependencies import company_service_dep
from app.api.dependencies import async_db_dep
from app.core.config import settings
from app.core.security import create_access_token
from app.db.base import get_async_db
from app.schemas.user import UserLogin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
async def register_step1(
        data: UserCreateStep1,
        db: async_db_dep
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    await auth_service.register_step1(data)
    return {"message": "Registration email sent"}


@router.post("/register/step2", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register_step2(
        data: UserCreateStep2,
        db: async_db_dep
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.register_step2(data)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/verify-token/")
async def verify_token(
        token: token_data_dep,
        company_service: company_service_dep,
) -> VerifyTokenResponse:
    company = await company_service.get_company_by_user_id(token.user_id)
    return VerifyTokenResponse(
        is_valid=token.user_id is not None,
        logo=company.logo,
        company_name=company.name,
    )
@router.get("/registration/verify-token/{token}")
async def verify_token(
        token: str,
        auth_service: AuthServiceDep
) -> dict:
    is_valid = await auth_service.verify_token(token)
    return {"is_valid": is_valid}

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: async_db_dep
):
    """
    Login user with INN and password.
    Password must be at least 8 characters long.
    """
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.authenticate_user_by_inn(user_data.inn, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect INN or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/token", response_model=Token)
async def login(
        db: async_db_dep,
        username: str = Form(...),
        password: str = Form(...),
        grant_type: Optional[str] = Form(None),
):
    """
    Login user with username (INN) and password.

    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.authenticate_user_by_inn(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect INN or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=User)
async def get_current_user(
    request: Request,
    db: async_db_dep
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax"
    )
    return {"message": "Successfully logged out"}
