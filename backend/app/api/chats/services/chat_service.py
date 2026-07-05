from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.chats.models.chat import Chat
from app.api.chats.repositories.chat_repository import ChatRepository
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
            await self._sync_chat_participants(
                existing_chat.id,
                current_company_id,
                current_user_id,
                chat_data.participant_company_id,
            )
            updated_chat = await self.repository.get_chat_by_id(existing_chat.id)
            return await self._format_chat_response(updated_chat, current_company_id)
        participant_company = await self.repository.get_company_by_id(chat_data.participant_company_id)
        if not participant_company:
            raise ValueError(f"Company with ID {chat_data.participant_company_id} not found")

        participant_user_id = await self.repository.get_company_user_id(chat_data.participant_company_id)
        if not participant_user_id:
            raise ValueError(f"No user found for company ID {chat_data.participant_company_id}")

        # Создаем новый чат
        chat = await self.repository.create_chat(title=chat_data.title)

        # Добавляем участников
        await self.repository.ensure_participant(chat.id, current_company_id, current_user_id)
        await self.repository.ensure_participant(
            chat.id, chat_data.participant_company_id, participant_user_id
        )

        # Получаем обновленный чат с участниками
        updated_chat = await self.repository.get_chat_by_id(chat.id)
        return await self._format_chat_response(updated_chat, current_company_id)

    async def get_user_chats(self, user_id: int, company_id: Optional[int] = None) -> List[ChatListResponse]:
        """Получает все чаты пользователя (по user_id и company_id)."""
        chats = await self.repository.get_user_chats(user_id, company_id)
        return [
            await self._format_chat_list_response(chat, company_id)
            for chat in chats
        ]

    async def get_chat_by_id(self, chat_id: int) -> Optional[ChatResponse]:
        """Получает чат по ID"""
        chat = await self.repository.get_chat_by_id(chat_id)
        if not chat:
            return None
        return await self._format_chat_response(chat)

    async def create_chat_by_slug(self, current_user_id: int, current_company_id: int,
                                  participant_slug: str) -> ChatResponse:
        """Создает чат по slug участника"""
        # Находим компанию по slug
        participant_company = await self.repository.get_company_by_slug(participant_slug)
        if not participant_company:
            raise ValueError(f"Company with slug {participant_slug} not found")

        participant_user_id = await self.repository.get_company_user_id(participant_company.id)
        if not participant_user_id:
            raise ValueError(f"No user found for company {participant_slug}")

        # Проверяем, существует ли уже чат
        existing_chat = await self.repository.find_existing_chat(current_company_id, participant_company.id)

        if existing_chat:
            await self._sync_chat_participants(
                existing_chat.id,
                current_company_id,
                current_user_id,
                participant_company.id,
            )
            updated_chat = await self.repository.get_chat_by_id(existing_chat.id)
            return await self._format_chat_response(updated_chat, current_company_id)

        # Создаем новый чат
        chat = await self.repository.create_chat()

        # Добавляем участников
        await self.repository.ensure_participant(chat.id, current_company_id, current_user_id)
        await self.repository.ensure_participant(chat.id, participant_company.id, participant_user_id)

        # Получаем обновленный чат с участниками
        updated_chat = await self.repository.get_chat_by_id(chat.id)
        return await self._format_chat_response(updated_chat, current_company_id)

    async def _sync_chat_participants(
        self,
        chat_id: int,
        current_company_id: int,
        current_user_id: int,
        other_company_id: int,
    ) -> None:
        """Привязать актуальных пользователей к существующему чату между компаниями."""
        await self.repository.ensure_participant(chat_id, current_company_id, current_user_id)
        other_user_id = await self.repository.get_company_user_id(other_company_id)
        if other_user_id:
            await self.repository.ensure_participant(chat_id, other_company_id, other_user_id)

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

    async def _format_chat_list_response(
        self, chat: Chat, company_id: Optional[int] = None
    ) -> ChatListResponse:
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

        unread_count = 0
        if company_id is not None:
            unread_count = await self.repository.count_unread_for_chat(chat.id, company_id)

        return ChatListResponse(
            id=chat.id,
            title=chat.title,
            is_group=chat.is_group,
            participants=participants,
            last_message=last_message,
            unread_count=unread_count,
            created_at=chat.created_at,
            updated_at=chat.updated_at
        )

    async def mark_chat_as_read(self, chat_id: int, reader_company_id: int) -> list[int]:
        """Пометить входящие сообщения чата прочитанными."""
        return await self.repository.mark_incoming_messages_read(chat_id, reader_company_id)

    async def send_message(
        self,
        chat_id: int,
        sender_company_id: int,
        sender_user_id: int,
        content: str,
    ):
        """Сохранить сообщение в чат и разослать подписчикам WebSocket."""
        from app.api.messages.models.message import Message

        message = Message(
            chat_id=chat_id,
            sender_company_id=sender_company_id,
            sender_user_id=sender_user_id,
            content=content,
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        try:
            from app.api.chats.websocket_manager import chat_manager

            message_data = {
                "id": message.id,
                "chat_id": message.chat_id,
                "sender_company_id": message.sender_company_id,
                "sender_user_id": message.sender_user_id,
                "content": message.content,
                "file_path": None,
                "file_name": None,
                "file_size": None,
                "file_type": None,
                "is_read": message.is_read,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
            }
            chat = await self.repository.get_chat_by_id(chat_id)
            participant_user_ids = (
                {p.user_id for p in chat.participants} if chat else None
            )
            await chat_manager.send_message_to_chat(
                chat_id,
                message_data,
                sender_user_id,
                participant_user_ids=participant_user_ids,
            )
        except Exception as exc:
            from app_logging.logger import logger

            logger.warning("WebSocket broadcast failed for chat %s: %s", chat_id, exc)

        return message
