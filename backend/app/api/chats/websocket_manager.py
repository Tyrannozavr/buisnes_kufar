import asyncio
import datetime
import json
from typing import Dict, Set, Optional

from fastapi import WebSocket

from app_logging.logger import logger


def json_default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


class ChatWebSocketManager:
    def __init__(self):
        # {chat_id: {user_id: WebSocket}}
        self.chat_connections: Dict[int, Dict[int, WebSocket]] = {}
        # {user_id: {chat_id: WebSocket}}
        self.user_connections: Dict[int, Dict[int, WebSocket]] = {}
        # Глобальное присутствие на сайте: {user_id: WebSocket}
        self.presence_connections: Dict[int, WebSocket] = {}
        # Чаты пользователя для рассылки presence-событий
        self.user_presence_chat_ids: Dict[int, Set[int]] = {}

    def _is_user_online_anywhere(self, user_id: int) -> bool:
        if user_id in self.presence_connections:
            return True
        return bool(self.user_connections.get(user_id))

    async def _broadcast_chat_event(
        self,
        chat_id: int,
        message: dict,
        exclude_user_id: Optional[int] = None,
    ):
        """Событие чата — подписчикам WS чата и presence-подключениям участников."""
        await self.broadcast_to_chat(chat_id, message, exclude_user_id=exclude_user_id)

        for user_id, websocket in list(self.presence_connections.items()):
            if exclude_user_id and user_id == exclude_user_id:
                continue
            if chat_id not in self.user_presence_chat_ids.get(user_id, set()):
                continue
            await self.send_personal_message(message, websocket)

    async def _notify_user_online(self, user_id: int, chat_ids: Set[int]):
        for chat_id in chat_ids:
            await self._broadcast_chat_event(
                chat_id,
                {
                    "type": "user_online",
                    "chat_id": chat_id,
                    "user_id": user_id,
                },
                exclude_user_id=user_id,
            )

    async def _notify_user_offline_if_needed(self, user_id: int, chat_ids: Set[int]):
        if self._is_user_online_anywhere(user_id):
            return
        for chat_id in chat_ids:
            await self._broadcast_chat_event(
                chat_id,
                {
                    "type": "user_offline",
                    "chat_id": chat_id,
                    "user_id": user_id,
                },
                exclude_user_id=user_id,
            )

    async def connect_presence(
        self,
        websocket: WebSocket,
        user_id: int,
        chat_ids: Set[int],
    ):
        """Глобальное подключение: пользователь онлайн на сайте."""
        await websocket.accept()

        old_ws = self.presence_connections.get(user_id)
        if old_ws is not None and old_ws is not websocket:
            try:
                await old_ws.close()
            except Exception:
                pass

        was_online = self._is_user_online_anywhere(user_id)
        self.presence_connections[user_id] = websocket
        self.user_presence_chat_ids[user_id] = chat_ids

        logger.info("User %s connected to global presence (%s chats)", user_id, len(chat_ids))

        await self.send_personal_message(
            {
                "type": "presence_established",
                "user_id": user_id,
            },
            websocket,
        )

        if not was_online:
            await self._notify_user_online(user_id, chat_ids)

    def disconnect_presence(self, user_id: int):
        chat_ids = self.user_presence_chat_ids.pop(user_id, set())
        self.presence_connections.pop(user_id, None)

        logger.info("User %s disconnected from global presence", user_id)

        asyncio.create_task(self._notify_user_offline_if_needed(user_id, chat_ids))

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: int):
        """Подключение пользователя к конкретному чату (сообщения, typing)."""
        await websocket.accept()

        was_online = self._is_user_online_anywhere(user_id)

        if chat_id not in self.chat_connections:
            self.chat_connections[chat_id] = {}
        self.chat_connections[chat_id][user_id] = websocket

        if user_id not in self.user_connections:
            self.user_connections[user_id] = {}
        self.user_connections[user_id][chat_id] = websocket

        logger.info("User %s connected to chat %s", user_id, chat_id)

        await self.send_personal_message(
            {
                "type": "connection_established",
                "chat_id": chat_id,
                "user_id": user_id,
            },
            websocket,
        )

        if not was_online:
            await self._notify_user_online(user_id, {chat_id})

    def disconnect(self, chat_id: int, user_id: int):
        """Отключение пользователя от конкретного чата."""
        if chat_id in self.chat_connections and user_id in self.chat_connections[chat_id]:
            del self.chat_connections[chat_id][user_id]
            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]

        if user_id in self.user_connections and chat_id in self.user_connections[user_id]:
            del self.user_connections[user_id][chat_id]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info("User %s disconnected from chat %s", user_id, chat_id)

        asyncio.create_task(self._notify_user_offline_if_needed(user_id, {chat_id}))

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message, default=json_default))
        except Exception as e:
            logger.error("Error sending personal message: %s", e)

    async def broadcast_to_chat(
        self,
        chat_id: int,
        message: dict,
        exclude_user_id: Optional[int] = None,
    ):
        if chat_id not in self.chat_connections:
            return

        disconnected_users = []

        for user_id, websocket in self.chat_connections[chat_id].items():
            if exclude_user_id and user_id == exclude_user_id:
                continue

            try:
                await websocket.send_text(json.dumps(message, default=json_default))
            except Exception as e:
                logger.error(
                    "Error broadcasting to user %s in chat %s: %s",
                    user_id,
                    chat_id,
                    e,
                )
                disconnected_users.append(user_id)

        for user_id in disconnected_users:
            self.disconnect(chat_id, user_id)

    async def send_message_to_chat(self, chat_id: int, message_data: dict, sender_user_id: int):
        message = {
            "type": "new_message",
            "chat_id": chat_id,
            "message": message_data,
            "sender_user_id": sender_user_id,
        }

        await self._broadcast_chat_event(chat_id, message, exclude_user_id=sender_user_id)

    async def send_messages_read(
        self,
        chat_id: int,
        message_ids: list[int],
        reader_user_id: int,
    ):
        """Уведомить участников, что входящие сообщения прочитаны."""
        if not message_ids:
            return
        message = {
            "type": "messages_read",
            "chat_id": chat_id,
            "message_ids": message_ids,
            "reader_user_id": reader_user_id,
        }
        await self._broadcast_chat_event(chat_id, message, exclude_user_id=reader_user_id)

    async def send_typing_indicator(self, chat_id: int, user_id: int, is_typing: bool):
        message = {
            "type": "typing_indicator",
            "chat_id": chat_id,
            "user_id": user_id,
            "is_typing": is_typing,
        }

        await self.broadcast_to_chat(chat_id, message, exclude_user_id=user_id)

    def is_user_online_in_chat(self, chat_id: int, user_id: int) -> bool:
        if user_id in self.presence_connections:
            return True
        if chat_id in self.chat_connections:
            return user_id in self.chat_connections[chat_id]
        return False

    def get_online_users_in_chat(
        self,
        chat_id: int,
        participant_user_ids: Optional[Set[int]] = None,
    ) -> Set[int]:
        if participant_user_ids is None:
            participant_user_ids = set()
            if chat_id in self.chat_connections:
                participant_user_ids.update(self.chat_connections[chat_id].keys())
            participant_user_ids.update(self.presence_connections.keys())
            return participant_user_ids

        online: Set[int] = set()
        for user_id in participant_user_ids:
            if self.is_user_online_in_chat(chat_id, user_id):
                online.add(user_id)
        return online


chat_manager = ChatWebSocketManager()
