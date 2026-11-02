# TODO: Dependabot Security Alerts

Источник: GitHub → Security → Dependabot alerts (`Tyrannozavr/buisnes_kufar`).  
Цель: обновить зависимости в `backend/poetry.lock` / `frontend/package-lock.json`.

Статус: ✅ critical/high закрыты локально (2026-11-02) · ⏳ moderate/low остатки · после мержа Dependabot должен auto-dismiss

## Что сделано (2026-11-02)

### Backend (`pyproject.toml` / `poetry.lock`)

| Было | Стало | Заметка |
|------|-------|---------|
| `python-jose` 3.5.0 (critical, **нет патча**) | удалён → **PyJWT 2.15.1** | миграция в `app/core/security.py` |
| `anyio` &lt; 4.14.2 | **4.16.0** | TLS/IDNA |
| `PyJWT` ≤ 2.13 | **2.15.1** | algorithm confusion / PEM |
| `urllib3` | **2.8.0** | streaming / decompression |
| `starlette` 0.46 | **1.10.0** (через FastAPI 0.162) | Host / Range / form DoS |
| `python-multipart` 0.0.20 | **0.0.31** | file write / DoS |
| `sqladmin` 0.20.1 | **0.27.2** | sortBy / ajax_lookup |
| `cryptography` | **50.0.2** | OpenSSL / path-building |
| `Mako` | **1.4.3** | path traversal |
| `lxml` | **6.1.3** | XXE iterparse |
| `pyasn1` | **0.6.5** | OID DoS |
| `idna` | **3.20** | encode bypass |
| `aiosmtplib` | **5.1.3** | SMTP CRLF |
| `pydantic-settings` | **2.16.2** | secrets_dir symlink |
| `pytest` | **9.2.0** | tmpdir |
| `ecdsa` (transitive jose) | **удалён** | ушёл вместе с python-jose |
| `sqlalchemy` | **2.0.55** + greenlet | pinned `&lt;2.1` (2.1 ломал asyncio без greenlet) |

### Frontend (`package.json` overrides + bumps)

| Пакет | Стало |
|-------|-------|
| `nuxt` | **3.21.11** |
| `@nuxt/devtools` | **3.4.4** (override) |
| `seroval` | **1.7.6** |
| `shell-quote` | **1.12.0** |
| `tar` | **7.5.22** |
| `simple-git` | **≥4.0.1** (override) |
| `sharp` | **0.35.5** |
| `@xmldom/xmldom` | **0.8.15** |
| `vite` / `devalue` / `ws` / `svgo` / `launch-editor` / `source-map-js` / `prosemirror-view` / `@vue/server-renderer` | patched via overrides |
| `@tiptap/*` | **3.32.2** |
| `node-forge` | **1.4.2** |
| `brace-expansion@1` / `@5` | **1.1.21** / **5.0.12** |

`npm audit` после фикса: **0 critical, 0 high**, ~41 moderate/low (в основном eslint / `@nuxt/ui` major / route-rules Nuxt — нужны major-апгрейды).

### Проверки

- Backend: JWT encode/decode OK, `/docs` 200, login `seller@gmail.com` OK.
- Frontend: `npm run build` ✅.
- Pytest: 68 passed на ядре; известные падения **не из security-diff** (нет роута `documents/form`, enum `Покупатель`, auth override в units, FK teardown в checkout).

## Осталось (moderate / без патча)

| Пакет | Почему осталось |
|-------|-----------------|
| `diskcache` | pickle deserialization — **патча нет**, нужен отказ от pickle / замена |
| Nuxt route-rules / islands / eslint-utils | часто чинятся только major (`nuxt@4`, `@nuxt/ui@4`) |
| Dev-only eslint/minimatch | low risk в prod-сборке |

## Как закрывать остатки

1. Backend: при новых GHSA — `poetry update <pkg>` в контейнере `backend`.
2. Frontend: bump + `overrides` в `package.json` → `npm install` → `npm run build`.
3. После push в default branch — проверить, что Dependabot alerts стали Resolved.
4. Major Nuxt 4 / `@nuxt/ui` 4 — отдельная задача (ломающие изменения).
