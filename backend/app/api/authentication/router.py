from fastapi import APIRouter, Response, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from app.api.authentication.dependencies import AuthServiceDep
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import User, UserCreateStep1, UserCreateStep2
from app.api.authentication.services.auth_service import AuthService
from app.api.dependencies import get_async_db
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserLogin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
async def register_step1(
        data: UserCreateStep1,
        db: get_async_db
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    await auth_service.register_step1(data)
    return {"message": "Registration email sent"}


@router.post("/register/step2", status_code=status.HTTP_201_CREATED)
async def register_step2(
        data: UserCreateStep2,
        response: Response,
        db: get_async_db
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
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


@router.post("/login", response_model=dict)
async def login(
    response: Response,
    user_data: UserLogin,
    db: get_async_db
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
    
    # Set HTTP-only cookie with the token
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,  # True in production
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return {"message": "Successfully logged in"}


@router.get("/me", response_model=User)
async def get_current_user(
    request: Request,
    db: get_async_db
):
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
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
