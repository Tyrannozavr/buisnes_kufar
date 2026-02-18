"""
Простой скрипт для проверки работы MinIO/S3-конфига бэкенда.

Запуск (из корня проекта, через docker-compose.dev):
  docker compose -f docker-compose.dev.yml exec backend poetry run python helpers/test_minio.py

Или локально (если backend запускаешь без Docker):
  cd backend
  poetry run python helpers/test_minio.py
"""

from app.core.config import settings
from app.core import s3


def main() -> None:
    print(f"S3_ENABLED = {settings.S3_ENABLED}")
    print(f"S3_ENDPOINT_URL = {settings.S3_ENDPOINT_URL!r}")
    print(f"S3_BUCKET = {settings.S3_BUCKET!r}")

    if not settings.S3_ENABLED:
        print("S3 не сконфигурирован (нет bucket или ключей). Проверь переменные окружения.")
        return

    test_content = b"hello from test_minio"
    test_filename = "test_minio.txt"
    deal_id = 0  # Тестовый deal_id, в БД не используется

    print("Пробуем загрузить файл в S3/MinIO...")
    key = s3.upload_document(
        deal_id=deal_id,
        filename=test_filename,
        content=test_content,
        content_type="text/plain",
    )
    print(f"Файл загружен. S3 key = {key!r}")

    url = s3.get_presigned_download_url(key)
    print(f"Presigned URL для скачивания:\n{url}")

    print("Пробуем удалить файл из S3/MinIO...")
    ok = s3.delete_document(key)
    print(f"Удаление: {'OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()

