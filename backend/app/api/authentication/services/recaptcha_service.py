import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class RecaptchaService:
    """Сервис для проверки reCAPTCHA v3"""

    def __init__(self):
        self.secret_key = settings.RECAPTCHA_SECRET_KEY
        self.min_score = settings.RECAPTCHA_MIN_SCORE
        self.verify_url = "https://www.google.com/recaptcha/api/siteverify"

    async def verify_recaptcha(self, token: str, remote_ip: str = None, origin: str = None) -> bool:
        """
        Проверяет токен reCAPTCHA v3
        
        Args:
            token: Токен reCAPTCHA от клиента
            remote_ip: IP адрес клиента (опционально)
            origin: Origin заголовок для проверки домена (опционально)
            
        Returns:
            bool: True если проверка прошла успешно
        """
        # Пропускаем проверку reCAPTCHA для localhost:3000 (разработка)
        if origin and ('localhost:3000' in origin or '127.0.0.1:3000' in origin):
            return True
            
        # Пропускаем проверку если токен не передан (для localhost)
        if not token:
            # Если это localhost, разрешаем без токена
            if origin and ('localhost' in origin or '127.0.0.1' in origin):
                return True
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="reCAPTCHA token is required"
            )

        # Подготавливаем данные для отправки
        data = {
            "secret": self.secret_key,
            "response": token
        }

        if remote_ip:
            data["remoteip"] = remote_ip

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.verify_url, data=data)
                result = response.json()

                if not result.get("success", False):
                    error_codes = result.get("error-codes", [])
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"reCAPTCHA verification failed: {', '.join(error_codes)}"
                    )

                # Проверяем балл
                score = result.get("score", 0.0)
                if score < self.min_score:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"reCAPTCHA score too low: {score} (minimum: {self.min_score})"
                    )

                return True

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify reCAPTCHA: {str(e)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unexpected error during reCAPTCHA verification: {str(e)}"
            )


# Создаем экземпляр сервиса
recaptcha_service = RecaptchaService()
