from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    # Convert minutes to timedelta
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Token is invalid")


def get_current_user_id_from_token(token: str) -> UUID:
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Token is invalid")
        return UUID(user_id)
    except (JWTError, ValueError):
        raise ValueError("Token is invalid")


EMAIL_UNSUBSCRIBE_PURPOSE = "email_notifications_unsubscribe"
# Ссылка в письме должна жить долго — пользователь может отписаться позже
EMAIL_UNSUBSCRIBE_EXPIRE_DAYS = 365 * 2


def create_email_unsubscribe_token(user_id: int) -> str:
    """Подписанный токен для одноразовой отписки от email-уведомлений."""
    expire = datetime.utcnow() + timedelta(days=EMAIL_UNSUBSCRIBE_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "purpose": EMAIL_UNSUBSCRIBE_PURPOSE,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_email_unsubscribe_token(token: str) -> Optional[int]:
    """Вернуть user_id при валидном токене отписки, иначе None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("purpose") != EMAIL_UNSUBSCRIBE_PURPOSE:
            return None
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except (JWTError, ValueError, TypeError):
        return None
