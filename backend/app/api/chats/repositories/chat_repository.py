from typing import List, Optional

from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.authentication.models import User
from app.api.authentication.models.roles_positions import UserRole
from app.api.chats.models.chat import Chat
from app.api.chats.models.chat_participant import ChatParticipant
from app.api.company.models.company import Company
from app.api.messages.models.message import Message


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

    async def ensure_participant(
        self, chat_id: int, company_id: int, user_id: int, is_admin: bool = False
    ) -> ChatParticipant:
        """Участник чата для компании: добавить или обновить user_id (актуальный сотрудник)."""
        stmt = select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.company_id == company_id,
        )
        result = await self.db.execute(stmt)
        participant = result.scalar_one_or_none()

        if participant:
            if participant.user_id != user_id:
                participant.user_id = user_id
                await self.db.commit()
                await self.db.refresh(participant)
            return participant

        return await self.add_participant(chat_id, company_id, user_id, is_admin)

    async def add_participant(self, chat_id: int, company_id: int, user_id: int,
                              is_admin: bool = False) -> ChatParticipant:
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

    def _participant_options(self):
        return (
            joinedload(Chat.participants).joinedload(ChatParticipant.company),
            joinedload(Chat.participants).joinedload(ChatParticipant.user),
        )

    async def get_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        """Получает чат по ID с участниками (без полной истории сообщений)."""
        stmt = select(Chat).options(*self._participant_options()).where(Chat.id == chat_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_user_chats(self, user_id: int, company_id: Optional[int] = None) -> List[Chat]:
        """Чаты пользователя: по user_id и (если задано) по company_id компании."""
        stmt = (
            select(Chat)
            .join(ChatParticipant)
            .where(ChatParticipant.user_id == user_id)
            .options(*self._participant_options())
        )
        result = await self.db.execute(stmt)
        chats = list(result.unique().scalars().all())
        seen_ids = {chat.id for chat in chats}

        if company_id is not None:
            stmt_company = (
                select(Chat)
                .join(ChatParticipant)
                .where(ChatParticipant.company_id == company_id)
                .options(*self._participant_options())
            )
            company_result = await self.db.execute(stmt_company)
            for chat in company_result.unique().scalars().all():
                if chat.id not in seen_ids:
                    chats.append(chat)
                    seen_ids.add(chat.id)

        return chats

    async def get_company_chats(self, company_id: int) -> List[Chat]:
        """Получает все чаты компании"""
        stmt = select(Chat).join(ChatParticipant).where(
            ChatParticipant.company_id == company_id
        ).options(*self._participant_options())
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def find_existing_chat(self, company1_id: int, company2_id: int) -> Optional[Chat]:
        """Находит существующий чат между двумя компаниями"""
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
        ).options(*self._participant_options())
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_last_messages_for_chats(self, chat_ids: List[int]) -> dict[int, Message]:
        """Последнее сообщение по каждому чату (один запрос с DISTINCT ON)."""
        if not chat_ids:
            return {}
        # PostgreSQL DISTINCT ON
        stmt = (
            select(Message)
            .where(Message.chat_id.in_(chat_ids))
            .distinct(Message.chat_id)
            .order_by(Message.chat_id, Message.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return {msg.chat_id: msg for msg in result.scalars().all()}

    async def count_unread_for_chats(
        self, chat_ids: List[int], reader_company_id: int
    ) -> dict[int, int]:
        """Непрочитанные по списку чатов одним GROUP BY."""
        if not chat_ids:
            return {}
        stmt = (
            select(Message.chat_id, func.count(Message.id))
            .where(
                Message.chat_id.in_(chat_ids),
                Message.sender_company_id != reader_company_id,
                Message.is_read.is_(False),
            )
            .group_by(Message.chat_id)
        )
        result = await self.db.execute(stmt)
        return {chat_id: int(count) for chat_id, count in result.all()}

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

    async def get_company_user_id(self, company_id: int) -> Optional[int]:
        """Получает user_id владельца или первого пользователя компании (User.company_id -> Company)"""
        stmt = select(User.id).where(
            User.company_id == company_id,
            User.role == UserRole.OWNER
        ).limit(1)
        result = await self.db.execute(stmt)
        user_id = result.scalar_one_or_none()
        if user_id is not None:
            return user_id
        stmt = select(User.id).where(User.company_id == company_id).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получает пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def count_unread_for_chat(self, chat_id: int, reader_company_id: int) -> int:
        """Непрочитанные входящие сообщения для компании-получателя."""
        stmt = select(func.count(Message.id)).where(
            Message.chat_id == chat_id,
            Message.sender_company_id != reader_company_id,
            Message.is_read.is_(False),
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one() or 0)

    async def mark_incoming_messages_read(
        self, chat_id: int, reader_company_id: int
    ) -> list[int]:
        """Пометить прочитанными все входящие сообщения чата для компании."""
        stmt = select(Message).where(
            Message.chat_id == chat_id,
            Message.sender_company_id != reader_company_id,
            Message.is_read.is_(False),
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        message_ids: list[int] = []
        for message in messages:
            message.is_read = True
            message_ids.append(message.id)
        if message_ids:
            await self.db.commit()
        return message_ids
