from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, select, func

from app.api.chats.models.chat import Chat
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.company.models.company import Company
from app.api.authentication.models import User


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, title: Optional[str] = None, is_group: bool = False) -> Chat:
        """Создает новый чат"""
        chat = Chat(title=title, is_group=is_group)
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def add_participant(self, chat_id: int, company_id: int, user_id: int, is_admin: bool = False) -> ChatParticipant:
        """Добавляет участника в чат"""
        participant = ChatParticipant(
            chat_id=chat_id,
            company_id=company_id,
            user_id=user_id,
            is_admin=is_admin
        )
        self.db.add(participant)
        await self.db.commit()
        await self.db.refresh(participant)
        return participant

    async def get_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        """Получает чат по ID с участниками"""
        stmt = select(Chat).options(
            joinedload(Chat.participants).joinedload(ChatParticipant.company),
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
            joinedload(Chat.messages)
        ).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_chats(self, user_id: int) -> List[Chat]:
        """Получает все чаты пользователя"""
        stmt = select(Chat).join(ChatParticipant).where(
            ChatParticipant.user_id == user_id
        ).options(
            joinedload(Chat.participants).joinedload(ChatParticipant.company),
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
            joinedload(Chat.messages)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_company_chats(self, company_id: int) -> List[Chat]:
        """Получает все чаты компании"""
        stmt = select(Chat).join(ChatParticipant).where(
            ChatParticipant.company_id == company_id
        ).options(
            joinedload(Chat.participants).joinedload(ChatParticipant.company),
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
            joinedload(Chat.messages)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def find_existing_chat(self, company1_id: int, company2_id: int) -> Optional[Chat]:
        """Находит существующий чат между двумя компаниями"""
        # Находим чаты, где участвуют обе компании
        subquery = select(ChatParticipant.chat_id).where(
            ChatParticipant.company_id.in_([company1_id, company2_id])
        ).group_by(ChatParticipant.chat_id).having(
            func.count(ChatParticipant.chat_id) == 2
        ).subquery()

        stmt = select(Chat).where(
            and_(
                Chat.id.in_(subquery),
                Chat.is_group == False  # Только личные чаты
            )
        ).options(
            joinedload(Chat.participants).joinedload(ChatParticipant.company),
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
            joinedload(Chat.messages)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_company_by_slug(self, slug: str) -> Optional[Company]:
        """Получает компанию по slug"""
        stmt = select(Company).where(Company.slug == slug)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Получает компанию по ID"""
        stmt = select(Company).where(Company.id == company_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none() 