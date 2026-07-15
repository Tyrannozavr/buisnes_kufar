# Тестовые пользователи — пакет ТЗ_15

Базовые аккаунты счёта остаются ([../schet/test-users.md](../schet/test-users.md)).

## Дополнительно (seed этапа 5)

| Роль | Email | Пароль | Торговая деятельность |
|------|-------|--------|------------------------|
| Перевозчик | `carrier@gmail.com` | `123456` | Перевозчик |
| Экспедитор | `forwarder@gmail.com` | `123456` | Экспедитор |

```bash
docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_schet_test_users.py
```

## Куда зайти — §5.x

Пошагово: [manual-etap-05-checklist.md](manual-etap-05-checklist.md).
