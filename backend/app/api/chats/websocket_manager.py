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
        # Словарь для хранения подключений по чатам
        # {chat_id: {user_id: WebSocket}}
        self.chat_connections: Dict[int, Dict[int, WebSocket]] = {}
        # Словарь для хранения подключений пользователей
        # {user_id: {chat_id: WebSocket}}
        self.user_connections: Dict[int, Dict[int, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: int):
        """Подключение пользователя к чату"""
        await websocket.accept()

        # Добавляем подключение в чат
        if chat_id not in self.chat_connections:
            self.chat_connections[chat_id] = {}
        self.chat_connections[chat_id][user_id] = websocket

        # Добавляем подключение пользователя
        if user_id not in self.user_connections:
            self.user_connections[user_id] = {}
        self.user_connections[user_id][chat_id] = websocket

        logger.info(f"User {user_id} connected to chat {chat_id}")

        # Отправляем подтверждение подключения
        await self.send_personal_message({
            "type": "connection_established",
            "chat_id": chat_id,
            "user_id": user_id
        }, websocket)

        # Уведомляем других участников о подключении
        await self.broadcast_to_chat(chat_id, {
            "type": "user_online",
            "chat_id": chat_id,
            "user_id": user_id
        }, exclude_user_id=user_id)

    def disconnect(self, chat_id: int, user_id: int):
        """Отключение пользователя от чата"""
        # Удаляем из подключений чата
        if chat_id in self.chat_connections and user_id in self.chat_connections[chat_id]:
            del self.chat_connections[chat_id][user_id]
            if not self.chat_connections[chat_id]:
                del self.chat_connections[chat_id]

        # Удаляем из подключений пользователя
        if user_id in self.user_connections and chat_id in self.user_connections[user_id]:
            del self.user_connections[user_id][chat_id]
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        logger.info(f"User {user_id} disconnected from chat {chat_id}")

        # Уведомляем других участников об отключении
        asyncio.create_task(self.broadcast_to_chat(chat_id, {
            "type": "user_offline",
            "chat_id": chat_id,
            "user_id": user_id
        }, exclude_user_id=user_id))

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправка личного сообщения пользователю"""
        try:
            await websocket.send_text(json.dumps(message, default=json_default))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_chat(self, chat_id: int, message: dict, exclude_user_id: Optional[int] = None):
        """Отправка сообщения всем участникам чата"""
        if chat_id not in self.chat_connections:
            return

        disconnected_users = []

        for user_id, websocket in self.chat_connections[chat_id].items():
            if exclude_user_id and user_id == exclude_user_id:
                continue

            try:
                await websocket.send_text(json.dumps(message, default=json_default))
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id} in chat {chat_id}: {e}")
                disconnected_users.append(user_id)

        # Удаляем отключенных пользователей
        for user_id in disconnected_users:
            self.disconnect(chat_id, user_id)

    async def send_message_to_chat(self, chat_id: int, message_data: dict, sender_user_id: int):
        """Отправка нового сообщения в чат"""
        message = {
            "type": "new_message",
            "chat_id": chat_id,
            "message": message_data,
            "sender_user_id": sender_user_id
        }

        await self.broadcast_to_chat(chat_id, message, exclude_user_id=sender_user_id)

    async def send_typing_indicator(self, chat_id: int, user_id: int, is_typing: bool):
        """Отправка индикатора печати"""
        message = {
            "type": "typing_indicator",
            "chat_id": chat_id,
            "user_id": user_id,
            "is_typing": is_typing
        }

        await self.broadcast_to_chat(chat_id, message, exclude_user_id=user_id)

    def get_connected_users_in_chat(self, chat_id: int) -> Set[int]:
        """Получение списка подключенных пользователей в чате"""
        if chat_id not in self.chat_connections:
            return set()
        return set(self.chat_connections[chat_id].keys())

    def is_user_online_in_chat(self, chat_id: int, user_id: int) -> bool:
        """Проверка, онлайн ли пользователь в конкретном чате"""
        if chat_id not in self.chat_connections:
            return False
        return user_id in self.chat_connections[chat_id]

    def get_online_users_in_chat(self, chat_id: int) -> Set[int]:
        """Получение списка онлайн пользователей в чате"""
        return self.get_connected_users_in_chat(chat_id)


# Глобальный экземпляр менеджера
chat_manager = ChatWebSocketManager()
