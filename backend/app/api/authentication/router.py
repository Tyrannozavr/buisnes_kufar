from typing import Optional

from fastapi import APIRouter, Response, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordBearer

from app.api.authentication.dependencies import AuthServiceDep, token_data_dep
from app.api.authentication.repositories.user_repository import UserRepository
from app.api.authentication.schemas.user import User, UserCreateStep1, UserCreateStep2, UserUpdate, Token, VerifyTokenResponse, \
    ChangePasswordRequest, ChangeEmailRequest, ChangeEmailConfirmRequest, PasswordResetRequest, \
    PasswordResetConfirmRequest, PasswordRecoveryRequest, PasswordRecoveryVerifyRequest, PasswordRecoveryResetRequest
from app.api.authentication.services.auth_service import AuthService
from app.api.authentication.services.recaptcha_service import recaptcha_service
from app.api.company.dependencies import company_service_dep
from app.db.dependencies import async_db_dep
from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.user import UserLogin

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/register/step1", status_code=status.HTTP_201_CREATED)
async def register_step1(
        data: UserCreateStep1,
        request: Request,
        db: async_db_dep
):
    # Получаем IP адрес клиента
    client_ip = request.client.host if request.client else None
    
    # Получаем origin заголовок для проверки домена
    origin = request.headers.get("origin")

    # Проверяем reCAPTCHA
    await recaptcha_service.verify_recaptcha(data.recaptcha_token, client_ip, origin)

    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    await auth_service.register_step1(data)
    return {"message": "Registration email sent"}


@router.post("/register/step2", status_code=status.HTTP_201_CREATED, response_model=Token)
async def register_step2(
        data: UserCreateStep2,
        db: async_db_dep
):
    """
    Завершение регистрации пользователя.
    Создает пользователя с паролем и ИНН, а также создает компанию по умолчанию.
    """
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


@router.post("/verify-token")
async def verify_token(
        token: token_data_dep,
        company_service: company_service_dep,
) -> VerifyTokenResponse:
    print("Token is ", token)
    company = await company_service.get_company_by_user_id(token.user_id)
    return VerifyTokenResponse(
        is_valid=token.user_id is not None,
        logo=company.logo,
        company_name=company.name,
        company_slug=company.slug,
        company_id=company.id,
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
    Login user with email/phone and password.
    Password must be at least 8 characters long.
    """
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )

    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.authenticate_user_by_login(user_data.login, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
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
    Login user with username (email/phone) and password.

    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.authenticate_user_by_login(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/phone or password",
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


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
        password_data: ChangePasswordRequest,
        request: Request,
        db: async_db_dep
):
    """
    Change user password (requires authentication)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    success = await auth_service.change_password(user.id, password_data)
    return {"message": "Password changed successfully"}


@router.post("/request-email-change", status_code=status.HTTP_200_OK)
async def request_email_change(
        email_data: ChangeEmailRequest,
        request: Request,
        db: async_db_dep
):
    """
    Request email change (requires authentication)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )

    success = await auth_service.request_email_change(user.id, email_data)
    return {"message": "Email change confirmation sent"}


@router.post("/confirm-email-change", status_code=status.HTTP_200_OK)
async def confirm_email_change(
        confirm_data: ChangeEmailConfirmRequest,
        db: async_db_dep
):
    """
    Confirm email change (no authentication required, uses token)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.confirm_email_change(confirm_data.token)
    return {"message": "Email changed successfully"}


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
        reset_data: PasswordResetRequest,
        db: async_db_dep
):
    """
    Request password reset (no authentication required)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.request_password_reset(reset_data.email)
    return {"message": "Password reset email sent"}


@router.post("/confirm-password-reset", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
        reset_data: PasswordResetConfirmRequest,
        db: async_db_dep
):
    """
    Confirm password reset (no authentication required, uses token)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.confirm_password_reset(reset_data.token, reset_data.new_password)
    return {"message": "Password reset successfully"}


# Новые эндпоинты для восстановления пароля с кодами
@router.post("/recover-password", status_code=status.HTTP_200_OK)
async def recover_password(
        recovery_data: PasswordRecoveryRequest,
        db: async_db_dep
):
    """
    Request password recovery with code (no authentication required)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.request_password_recovery(recovery_data.email)
    return {"success": True, "message": "Код восстановления отправлен на ваш email"}


@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_recovery_code(
        verify_data: PasswordRecoveryVerifyRequest,
        db: async_db_dep
):
    """
    Verify password recovery code (no authentication required)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.verify_password_recovery_code(verify_data.email, verify_data.code)
    return {"success": True, "message": "Код подтвержден"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_with_code(
        reset_data: PasswordRecoveryResetRequest,
        db: async_db_dep
):
    """
    Reset password using recovery code (no authentication required)
    """
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    success = await auth_service.reset_password_with_code(reset_data.email, reset_data.code, reset_data.newPassword)
    return {"success": True, "message": "Пароль успешно изменен"}


# Тестовый эндпоинт для отладки (удалить в продакшене)
@router.get("/debug/password-hash/{inn}")
async def debug_password_hash(
        inn: str,
        password: str,
        db: async_db_dep
):
    """
    Debug endpoint to check password hashing (remove in production)
    """
    from app.core.security import get_password_hash, verify_password

    user_repo = UserRepository(session=db)
    user = await user_repo.get_user_by_inn(inn)

    if not user:
        return {"error": "User not found"}

    if not user.hashed_password:
        return {"error": "User has no password hash"}

    # Проверяем текущий пароль
    current_verify = verify_password(password, user.hashed_password)

    # Создаем новый хеш для сравнения
    new_hash = get_password_hash(password)

    return {
        "user_id": user.id,
        "user_email": user.email,
        "user_inn": user.inn,
        "current_hash": user.hashed_password,
        "new_hash": new_hash,
        "current_verify": current_verify,
        "new_verify": verify_password(password, new_hash)
    }


@router.get("/me", response_model=User)
async def get_my_profile(
        request: Request,
        db: async_db_dep
):
    """Получить профиль текущего пользователя"""
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


@router.put("/me", response_model=User)
async def update_my_profile(
        user_data: UserUpdate,
        request: Request,
        db: async_db_dep
):
    """Обновить профиль текущего пользователя"""
    auth_service = AuthService(user_repository=UserRepository(session=db), db=db)
    user = await auth_service.get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_repository = UserRepository(session=db)
    
    try:
        # Фильтруем только переданные поля
        update_data = {k: v for k, v in user_data.model_dump().items() if v is not None}
        
        updated_user = await user_repository.update_user_profile(user.id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return updated_user
        
    except ValueError as e:
        # Ошибка уникальности ИНН
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
