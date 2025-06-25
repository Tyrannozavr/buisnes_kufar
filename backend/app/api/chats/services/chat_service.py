from typing import List, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.chats.repositories.chat_repository import ChatRepository
from app.api.chats.models.chat import Chat
from app.api.chats.schemas.chat import ChatCreate, ChatResponse, ChatListResponse
from app.api.chats.schemas.chat_participant import ChatParticipantResponse


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ChatRepository(db)

    async def create_chat(self, current_user_id: int, current_company_id: int, chat_data: ChatCreate) -> ChatResponse:
        """Создает новый чат или возвращает существующий"""
        # Проверяем, существует ли уже чат между этими компаниями
        existing_chat = await self.repository.find_existing_chat(current_company_id, chat_data.participant_company_id)

        if existing_chat:
            return await self._format_chat_response(existing_chat, current_company_id)

        # Получаем компанию-участника для определения владельца
        participant_company = await self.repository.get_company_by_id(chat_data.participant_company_id)
        if not participant_company:
            raise ValueError(f"Company with ID {chat_data.participant_company_id} not found")

        # Создаем новый чат
        chat = await self.repository.create_chat(title=chat_data.title)
        
        # Добавляем участников
        # Первый участник - текущий пользователь и его компания
        await self.repository.add_participant(chat.id, current_company_id, current_user_id)
        # Второй участник - владелец компании-участника
        await self.repository.add_participant(chat.id, chat_data.participant_company_id, participant_company.user_id)
        
        # Получаем обновленный чат с участниками
        updated_chat = await self.repository.get_chat_by_id(chat.id)
        return await self._format_chat_response(updated_chat, current_company_id)

    async def get_user_chats(self, user_id: int) -> List[ChatListResponse]:
        """Получает все чаты пользователя"""
        chats = await self.repository.get_user_chats(user_id)
        return [await self._format_chat_list_response(chat) for chat in chats]

    async def get_chat_by_id(self, chat_id: int) -> Optional[ChatResponse]:
        """Получает чат по ID"""
        chat = await self.repository.get_chat_by_id(chat_id)
        if not chat:
            return None
        return await self._format_chat_response(chat)

    async def create_chat_by_slug(self, current_user_id: int, current_company_id: int, participant_slug: str) -> ChatResponse:
        """Создает чат по slug участника"""
        # Находим компанию по slug
        participant_company = await self.repository.get_company_by_slug(participant_slug)
        if not participant_company:
            raise ValueError(f"Company with slug {participant_slug} not found")

        # Проверяем, существует ли уже чат
        existing_chat = await self.repository.find_existing_chat(current_company_id, participant_company.id)
        
        if existing_chat:
            return await self._format_chat_response(existing_chat, current_company_id)

        # Создаем новый чат
        chat = await self.repository.create_chat()
        
        # Добавляем участников
        # Первый участник - текущий пользователь и его компания
        await self.repository.add_participant(chat.id, current_company_id, current_user_id)
        # Второй участник - владелец компании-участника
        await self.repository.add_participant(chat.id, participant_company.id, participant_company.user_id)
        
        # Получаем обновленный чат с участниками
        updated_chat = await self.repository.get_chat_by_id(chat.id)
        return await self._format_chat_response(updated_chat, current_company_id)

    async def _format_chat_response(self, chat: Chat, current_company_id: int = None) -> ChatResponse:
        """Форматирует чат для ответа"""
        participants = []
        for participant in chat.participants:
            participants.append(ChatParticipantResponse(
                id=participant.id,
                company_id=participant.company_id,
                user_id=participant.user_id,
                company_name=participant.company.name,
                company_slug=participant.company.slug,
                company_logo=participant.company.logo or "",
                user_name=f"{participant.user.first_name or ''} {participant.user.last_name or ''}".strip(),
                is_admin=participant.is_admin,
                joined_at=participant.joined_at
            ))
        
        return ChatResponse(
            id=chat.id,
            title=chat.title,
            is_group=chat.is_group,
            participants=participants,
            current_company_id=current_company_id,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )

    async def _format_chat_list_response(self, chat: Chat) -> ChatListResponse:
        """Форматирует чат для списка чатов"""
        participants = []
        for participant in chat.participants:
            participants.append(ChatParticipantResponse(
                id=participant.id,
                company_id=participant.company_id,
                user_id=participant.user_id,
                company_name=participant.company.name,
                company_slug=participant.company.slug,
                company_logo=participant.company.logo or "",
                user_name=f"{participant.user.first_name or ''} {participant.user.last_name or ''}".strip(),
                is_admin=participant.is_admin,
                joined_at=participant.joined_at
            ))
        
        # Получаем последнее сообщение
        last_message = None
        if chat.messages:
            last_msg = max(chat.messages, key=lambda x: x.created_at)
            last_message = {
                "id": last_msg.id,
                "content": last_msg.content,
                "created_at": last_msg.created_at.isoformat()
            }
        
        return ChatListResponse(
            id=chat.id,
            title=chat.title,
            is_group=chat.is_group,
            participants=participants,
            last_message=last_message,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        ) 