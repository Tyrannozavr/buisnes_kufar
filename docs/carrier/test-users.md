# Тестовые пользователи — ТЗ_Перевозчик

**UI:** http://localhost  
**Пароль везде:** `123456`

| Роль | Email | Компания |
|------|-------|----------|
| Поставщик / клиент | `seller@gmail.com` | ООО Поставщик Тест |
| Покупатель | `buyer@gmail.com` | ООО Покупатель Тест |
| Перевозчик | `carrier@gmail.com` | test-carrier-tz15 |
| Экспедитор | `forwarder@gmail.com` | test-forwarder-tz15 |
| Разработчик (алиас поставщика) | `dmitiry40647274@gmail.com` | ООО Поставщик Тест |

Пересоздать:

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_schet_test_users.py
```

Подробные сценарии: [manual-step-by-step-acceptance.md](manual-step-by-step-acceptance.md).
