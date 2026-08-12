# Тестовые пользователи — ТЗ_Перевозчик

**UI:** http://localhost (логин: http://localhost/auth/login)  
**Пароль везде:** `123456`

| Роль | Email | Компания |
|------|-------|----------|
| Поставщик / клиент | `seller@gmail.com` | ООО Поставщик Тест |
| Покупатель | `buyer@gmail.com` | ООО Покупатель Тест |
| Перевозчик | `carrier@gmail.com` | ООО Перевозчик Тест |
| Экспедитор | `forwarder@gmail.com` | ООО Экспедитор Тест |
| Разработчик (алиас поставщика) | `dmitiry40647274@gmail.com` | ООО Поставщик Тест |

**Seed флота перевозчика:** ТС `Volvo FH · А123ВС 77`, водитель `Иванов Пётр Сергеевич`.

Пересоздать:

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_schet_test_users.py
```

Подробные сценарии: [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md).  
Оплата: [payment-and-schedule.md](payment-and-schedule.md).
