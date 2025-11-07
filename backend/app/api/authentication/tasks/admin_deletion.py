from datetime import datetime, timedelta
from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.authentication.repositories.employee_repository import EmployeeRepository
from app.api.authentication.models.employee import EmployeeStatus
from app_logging.logger import logger

# Инициализация Celery (нужно будет настроить в основном приложении)
celery_app = Celery('admin_deletion')


@celery_app.task
def process_admin_deletions():
    """Задача для обработки ожидающих удаления администраторов"""
    logger.info("Starting admin deletion processing task")
    
    # Здесь нужно будет получить сессию БД
    # Пока что это заглушка
    try:
        # В реальном приложении здесь будет:
        # 1. Получение сессии БД
        # 2. Создание репозитория
        # 3. Обработка удалений
        
        logger.info("Admin deletion processing completed")
        return {"processed_count": 0, "message": "No deletions to process"}
    except Exception as e:
        logger.error(f"Error processing admin deletions: {str(e)}")
        raise


async def process_pending_admin_deletions(db_session: AsyncSession) -> int:
    """Обработать ожидающие удаления администраторов"""
    employee_repository = EmployeeRepository(session=db_session)
    
    try:
        # Получаем всех администраторов с запрошенным удалением
        pending_deletions = await employee_repository.get_pending_deletions()
        processed_count = 0
        
        for employee in pending_deletions:
            # Проверяем, прошло ли 48 часов
            if not employee.deletion_requested_at:
                continue
                
            time_diff = datetime.utcnow() - employee.deletion_requested_at
            if time_diff < timedelta(hours=48):
                continue
            
            # Проверяем, что удаление не было отклонено
            if employee.deletion_rejected_at:
                continue
            
            # Выполняем удаление
            success = await employee_repository.execute_admin_deletion(employee.id)
            if success:
                processed_count += 1
                logger.info(f"Executed deletion for admin {employee.id}")
        
        logger.info(f"Processed {processed_count} admin deletions")
        return processed_count
        
    except Exception as e:
        logger.error(f"Error processing pending admin deletions: {str(e)}")
        raise


def schedule_admin_deletion_check():
    """Запланировать проверку удалений администраторов"""
    # Эта функция будет вызываться периодически (например, каждый час)
    process_admin_deletions.delay()


# Настройка периодических задач
celery_app.conf.beat_schedule = {
    'process-admin-deletions': {
        'task': 'admin_deletion.process_admin_deletions',
        'schedule': 3600.0,  # Каждый час
    },
}
celery_app.conf.timezone = 'UTC'
