#!/usr/bin/env python3
"""
Скрипт для очистки базы данных от тестовых данных
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from app.db.base import AsyncSessionLocal


async def clear_test_data():
    """Очищает базу данных от тестовых данных"""
    print("🧹 Очистка базы данных от тестовых данных...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Удаляем данные в правильном порядке (с учетом внешних ключей)
            tables_to_clear = [
                "announcements",
                "products", 
                "company_officials",
                "users",
                "companies"
            ]
            
            for table in tables_to_clear:
                print(f"Очистка таблицы {table}...")
                await session.execute(text(f"DELETE FROM {table}"))
                await session.commit()
            
            print("✅ База данных очищена от тестовых данных")
            
        except Exception as e:
            print(f"❌ Ошибка при очистке базы данных: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(clear_test_data())

