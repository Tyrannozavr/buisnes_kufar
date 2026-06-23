# 🚀 TradeSynergy - B2B Платформа для торговли

Полнофункциональная B2B платформа для торговли товарами и услугами между компаниями, построенная на современном стеке технологий.

## 📋 Описание проекта

TradeSynergy - это комплексная платформа для ведения B2B торговли, включающая:
- **Каталог товаров и услуг** с детальными характеристиками
- **Систему заказов** с документооборотом
- **Личные кабинеты** для компаний-продавцов и покупателей
- **Систему чатов** для общения между контрагентами
- **Административную панель** для управления платформой

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **PostgreSQL** - основная база данных
- **SQLAlchemy** - ORM для работы с БД
- **Alembic** - система миграций
- **Celery + RabbitMQ** - фоновые задачи
- **Redis** - кэширование

### Frontend
- **Nuxt.js 3** - Vue.js фреймворк
- **TypeScript** - типизированный JavaScript
- **Tailwind CSS** - стилизация
- **Pinia** - управление состоянием

### DevOps
- **Docker & Docker Compose** - контейнеризация
- **Nginx** - веб-сервер и прокси
- **Let's Encrypt** - SSL сертификаты
- **GitHub Actions** - CI/CD

## 🚀 Быстрый старт

### Разработка (Development)

```bash
# Клонирование репозитория
git clone <repository-url>
cd buisnes_kufar

# Запуск всех сервисов для разработки
docker-compose -f docker-compose.dev.yml up -d

# Проверка статуса сервисов
docker-compose -f docker-compose.dev.yml ps
```

**Доступ к сервисам:**
- 🌐 **Основной сайт**: http://localhost
- 📚 **API документация**: http://localhost:8000/docs
- ⚙️ **Админка**: http://localhost:8000/admin
- 🗄️ **PgAdmin**: http://localhost:5050 (admin@tradesynergy.dev / admin123)
- 🔧 **Прямой доступ к фронтенду**: http://localhost:3000
- 🔌 **Прямой доступ к API**: http://localhost:8000

### Продакшн (Production)

```bash
# Запуск всех сервисов
docker compose up -d

# Применение миграций
./scripts/run_migrations.sh

# Проверка статуса
docker compose ps
```

## 📚 Документация

### 🏗 Архитектура и настройка
- [**Быстрый старт**](docs/QUICK_START.md) - инструкция по запуску RabbitMQ и Celery
- [**Разработка**](docs/README-DEV.md) - подробное руководство по Docker Compose для разработки
- [**Локальное тестирование**](docs/README.local-testing.md) - тестирование с nginx

### 🔧 Системы и компоненты
- [**Celery и RabbitMQ**](docs/CELERY_SETUP.md) - настройка фоновых задач
- [**Миграции базы данных**](docs/MIGRATIONS_NEW_SYSTEM.md) - система миграций через отдельный контейнер
- [**Настройка миграций**](docs/MIGRATIONS_SETUP.md) - автоматическое применение миграций Alembic
- [**reCAPTCHA v3**](docs/RECAPTCHA_SETUP.md) - настройка защиты от ботов

### 📊 Данные и тестирование
- [**Дамп базы данных**](docs/DATABASE_DUMP_README.md) - полный дамп с тестовыми данными
- [**Отчет о тестировании**](docs/TESTING_REPORT.md) - результаты тестирования системы заказов

### 🛠 Разработка и изменения
- [**Резюме изменений**](docs/CHANGES_SUMMARY.md) - система загрузки изображений продуктов
- [**Реализация заказов**](docs/ORDERS_IMPLEMENTATION.md) - полная система управления заказами
- [**Анализ ошибок 404**](docs/404_ERROR_ANALYSIS.md) - комплексный анализ проблем с маршрутизацией

### 📋 Техническое задание и активная разработка

- [**ТЗ: раздел «Счет» (индекс)**](docs/TZ_SCET_RASSHIRENNOE.md) — scope, этапы, ссылки; **текущая работа: этап 1**
- [Этап 1 — доработки Сергея (10k)](docs/schet/etap-01-dorabotki-sergeya.md)
- [Этап 2 — счет на оплату (20k)](docs/schet/etap-02-schet-na-oplatu.md)
- [Этап 3 — «Создать счет» + договор поставки (20k)](docs/schet/etap-03-sozdanie-scheta-dogovor-postavki.md)
- [Этап 4 — счет-договор и оферта (20k)](docs/schet/etap-04-schet-dogovor-oferta.md)
- [Сверка с Git / что влито](docs/schet/git-status.md)
- [**ТЗ Расширение (старый текст)**](docs/ТЗ_Расширение.txt) — исходное ТЗ на расширение функционала

## 🗂 Структура проекта

```
buisnes_kufar/
├── backend/                 # Backend приложение (FastAPI)
│   ├── app/                # Основной код приложения
│   ├── alembic/            # Миграции базы данных
│   └── uploads/            # Загруженные файлы
├── frontend/               # Frontend приложение (Nuxt.js)
│   ├── components/         # Vue компоненты
│   ├── pages/             # Страницы приложения
│   └── plugins/           # Nuxt плагины
├── nginx/                  # Конфигурация Nginx
├── scripts/               # Скрипты для развертывания
├── docs/                  # 📚 Документация проекта
├── docker-compose.yml     # Production конфигурация
└── docker-compose.dev.yml # Development конфигурация
```

## 🔧 Основные команды

### Разработка
```bash
# Запуск в режиме разработки
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f

# Перезапуск сервиса
docker-compose -f docker-compose.dev.yml restart backend

# Выполнение команд в контейнере
docker-compose -f docker-compose.dev.yml exec backend bash
```

### Миграции
```bash
# Создание новой миграции
docker compose exec backend alembic revision --autogenerate -m "описание"

# Применение миграций
./scripts/run_migrations.sh

# Проверка статуса миграций
docker compose exec backend alembic current
```

### Celery (фоновые задачи)
```bash
# Мониторинг задач
curl http://localhost:8000/api/v1/celery/stats

# Ручной запуск задач
curl -X POST http://localhost:8000/api/v1/celery/tasks/refresh-all-caches
```

## 🌐 Доступные сервисы

### В режиме разработки
- **Frontend**: http://localhost:3000 (Nuxt dev server)
- **Backend**: http://localhost:8000 (FastAPI)
- **Database**: localhost:5432 (PostgreSQL)
- **PgAdmin**: http://localhost:5050
- **RabbitMQ Management**: http://localhost:15672

### В продакшне
- **Основной сайт**: https://tradesynergy.ru
- **API**: https://tradesynergy.ru/api
- **Документация API**: https://tradesynergy.ru/docs
- **Админка**: https://tradesynergy.ru/admin

## 🔐 Учетные данные по умолчанию

### База данных
- **Host**: localhost:5432
- **Database**: postgres
- **Username**: postgres
- **Password**: postgres

### PgAdmin (только в dev режиме)
- **Email**: admin@tradesynergy.dev
- **Password**: admin123

### RabbitMQ Management
- **Username**: admin
- **Password**: admin123

## 🚨 Устранение неполадок

### Проблемы с запуском
1. Проверьте, что все порты свободны
2. Убедитесь, что Docker запущен
3. Проверьте логи: `docker-compose logs -f`

### Проблемы с базой данных
1. Проверьте статус: `docker-compose ps db`
2. Примените миграции: `./scripts/run_migrations.sh`
3. Проверьте подключение через PgAdmin

### Проблемы с Celery
1. Проверьте RabbitMQ: http://localhost:15672
2. Проверьте логи worker: `docker-compose logs celery-worker`
3. Перезапустите сервисы: `docker-compose restart celery-worker celery-beat`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте [документацию](docs/) в директории `docs/`
2. Изучите логи сервисов
3. Создайте issue в репозитории

## 📄 Лицензия

Проект разработан для внутреннего использования.

---

**Статус проекта**: ✅ Активная разработка  
**Последнее обновление**: Октябрь 2025  
**Версия**: 1.0.0
