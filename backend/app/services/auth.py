from app.repositories.user import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate_user(self, telegram_id: str):
        # Здесь будет логика аутентификации
        pass