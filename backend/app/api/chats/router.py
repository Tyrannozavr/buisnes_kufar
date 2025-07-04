import os
from datetime import datetime
from typing import List, Optional
import json

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.dependencies import token_data_dep, current_user_dep
from app.api.authentication.models import User
from app.api.chats.schemas.chat import ChatCreate, ChatResponse, ChatListResponse
from app.api.chats.schemas.chat_participant import ChatParticipantResponse
from app.api.chats.services.chat_service import ChatService
from app.api.company.models.company import Company
from app.api.messages.models.message import Message
from app.db.dependencies import async_db_dep, get_async_db
from app.api.chats.websocket_manager import chat_manager
from app.core.security import decode_token
from app_logging.logger import logger

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def create_chat(
        chat_data: ChatCreate,
        db: async_db_dep,
        current_user: current_user_dep,

):
    """Создает новый чат или возвращает существующий"""
    # Получаем пользователя по ID из токена

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем компанию текущего пользователя
    result = await db.execute(
        select(Company).where(Company.user_id == current_user.id)
    )
    current_company = result.scalar_one_or_none()

    if not current_company:
        raise HTTPException(status_code=404, detail="Company not found for current user")

    chat_service = ChatService(db)
    try:
        chat = await chat_service.create_chat(current_user.id, current_company.id, chat_data)
        return chat
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/by-slug/{participant_slug}", response_model=ChatResponse)
async def create_chat_by_slug(
        participant_slug: str,
        db: async_db_dep,
        current_user: current_user_dep,

):
    """Создает чат по slug участника"""
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем компанию текущего пользователя
    result = await db.execute(
        select(Company).where(Company.user_id == current_user.id)
    )
    current_company = result.scalar_one_or_none()

    if not current_company:
        raise HTTPException(status_code=404, detail="Company not found for current user")

    chat_service = ChatService(db)
    try:
        chat = await chat_service.create_chat_by_slug(current_user.id, current_company.id, participant_slug)
        return chat
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("", response_model=List[ChatListResponse])
async def get_user_chats(
        db: async_db_dep,
        token_data: token_data_dep,

):
    """Получает все чаты пользователя"""
    chat_service = ChatService(db)
    chats = await chat_service.get_user_chats(token_data.user_id)
    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat_by_id(
        chat_id: int,
        db: async_db_dep,
        token_data: token_data_dep,

):
    """Получает чат по ID"""
    chat_service = ChatService(db)
    chat = await chat_service.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Проверяем, что пользователь является участником чата
    if not any(p.user_id == token_data.user_id for p in chat.participants):
        raise HTTPException(status_code=403, detail="Access denied: not a chat participant")

    return chat


# Утилита: проверка, что пользователь — участник чата
async def check_user_in_chat(chat_id: int, token_data, db: AsyncSession):
    chat_service = ChatService(db)
    chat = await chat_service.repository.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if not any(p.user_id == token_data.user_id for p in chat.participants):
        raise HTTPException(status_code=403, detail="Access denied: not a chat participant")
    return chat


@router.get("/{chat_id}/messages", response_model=List[dict])
async def get_chat_messages(
        chat_id: int,
        db: async_db_dep,
        token_data: token_data_dep,
):
    chat = await check_user_in_chat(chat_id, token_data, db)
    # Получаем сообщения чата
    stmt = select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    # Формируем ответ
    return [
        {
            "id": m.id,
            "chat_id": m.chat_id,
            "sender_company_id": m.sender_company_id,
            "sender_user_id": m.sender_user_id,
            "content": m.content,
            "file_path": m.file_path,
            "file_name": m.file_name,
            "file_size": m.file_size,
            "file_type": m.file_type,
            "is_read": m.is_read,
            "created_at": m.created_at,
            "updated_at": m.updated_at,
        }
        for m in messages
    ]


@router.get("/{chat_id}/files", response_model=List[dict])
async def get_chat_files(
        chat_id: int,
        db: async_db_dep,
        token_data: token_data_dep,
):
    chat = await check_user_in_chat(chat_id, token_data, db)
    # Получаем сообщения с файлами
    stmt = select(Message).where(Message.chat_id == chat_id, Message.file_path.isnot(None)).order_by(Message.created_at)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    # Формируем ответ
    return [
        {
            "message_id": m.id,
            "name": m.file_name,
            "url": m.file_path,
            "type": m.file_type,
            "size": m.file_size,
            "created_at": m.created_at,
        }
        for m in messages
    ]


@router.get("/{chat_id}/participants", response_model=List[ChatParticipantResponse])
async def get_chat_participants(
        chat_id: int,
        db: async_db_dep,
        token_data: token_data_dep,
):
    chat = await check_user_in_chat(chat_id, token_data, db)
    # Формируем ответ
    return [
        ChatParticipantResponse(
            id=p.id,
            company_id=p.company_id,
            user_id=p.user_id,
            company_name=p.company.name,
            company_slug=p.company.slug,
            company_logo=p.company.logo or "",
            user_name=f"{p.user.first_name or ''} {p.user.last_name or ''}".strip(),
            is_admin=p.is_admin,
            joined_at=p.joined_at
        )
        for p in chat.participants
    ]


@router.post("/{chat_id}/send", response_model=dict)
async def send_message(
        chat_id: int,
        db: async_db_dep,
        token_data: token_data_dep,
        content: str = Form(...),
        file: Optional[UploadFile] = File(None),
):
    """Отправляет сообщение в чат"""
    # Проверяем, что пользователь участвует в чате
    chat = await check_user_in_chat(chat_id, token_data, db)

    # Получаем пользователя по ID из токена
    result = await db.execute(
        select(User).where(User.id == token_data.user_id)
    )
    current_user = result.scalar_one_or_none()

    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем компанию текущего пользователя
    result = await db.execute(
        select(Company).where(Company.user_id == current_user.id)
    )
    current_company = result.scalar_one_or_none()

    if not current_company:
        raise HTTPException(status_code=404, detail="Company not found for current user")

    # Обрабатываем файл, если он есть
    file_path = None
    file_name = None
    file_size = None
    file_type = None

    if file:
        # Создаем директорию для файлов, если её нет
        upload_dir = "uploads/chat_files"
        os.makedirs(upload_dir, exist_ok=True)

        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
        file_name = f"{timestamp}_{file.filename}" if file.filename else f"{timestamp}_file"
        file_path = os.path.join(upload_dir, file_name)

        # Сохраняем файл
        with open(file_path, "wb") as buffer:
            content_file = await file.read()
            buffer.write(content_file)
            file_size = len(content_file)

        file_type = file.content_type or "application/octet-stream"

    # Создаем сообщение
    message = Message(
        chat_id=chat_id,
        sender_company_id=current_company.id,
        sender_user_id=current_user.id,
        content=content,
        file_path=file_path,
        file_name=file_name,
        file_size=file_size,
        file_type=file_type,
        is_read=False
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    # Отправляем уведомление через WebSocket
    message_data = {
        "id": message.id,
        "chat_id": message.chat_id,
        "sender_company_id": message.sender_company_id,
        "sender_user_id": message.sender_user_id,
        "content": message.content,
        "file_path": message.file_path,
        "file_name": message.file_name,
        "file_size": message.file_size,
        "file_type": message.file_type,
        "is_read": message.is_read,
        "created_at": message.created_at,
        "updated_at": message.updated_at,
    }
    
    await chat_manager.send_message_to_chat(chat_id, message_data, current_user.id)

    return message_data


@router.websocket("/{chat_id}/ws")
async def websocket_endpoint(websocket: WebSocket, chat_id: int):
    """WebSocket endpoint для чата"""
    try:
        # Получаем токен из query параметров
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001, reason="Token required")
            return
        
        # Декодируем токен
        try:
            payload = decode_token(token)
            user_id = int(payload.get("sub"))
        except Exception:
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        # Проверяем, что пользователь является участником чата
        async for db in get_async_db():
            chat_service = ChatService(db)
            chat = await chat_service.get_chat_by_id(chat_id)
            if not chat:
                await websocket.close(code=4004, reason="Chat not found")
                return
            
            if not any(p.user_id == user_id for p in chat.participants):
                await websocket.close(code=4003, reason="Access denied: not a chat participant")
                return
            break
        
        # Подключаем к чату
        await chat_manager.connect(websocket, chat_id, user_id)
        
        # Обрабатываем сообщения
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                message_type = message_data.get("type")
                
                if message_type == "typing":
                    # Отправляем индикатор печати
                    is_typing = message_data.get("is_typing", False)
                    await chat_manager.send_typing_indicator(chat_id, user_id, is_typing)
                
                elif message_type == "ping":
                    # Отвечаем на ping
                    await websocket.send_text(json.dumps({"type": "pong"}))
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        # Отключаем от чата
        if 'user_id' in locals() and 'chat_id' in locals():
            chat_manager.disconnect(chat_id, user_id)
