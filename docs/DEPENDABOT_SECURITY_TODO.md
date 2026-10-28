# TODO: Dependabot Security Alerts

Источник: GitHub → Security → Dependabot alerts (`Tyrannozavr/buisnes_kufar`), open alerts.  
Цель: обновить зависимости в `backend/poetry.lock` / `frontend/package-lock.json` (и при необходимости pin в `pyproject.toml` / `package.json`), закрыть алерты.

Статус: ⏳ не начато

## Critical

| # | Пакет | Тип | Lockfile | Описание |
|---|-------|-----|----------|----------|
| 232 | seroval | Transitive | frontend/package-lock.json | `seroval.fromJSON()` Promise resolver type confusion |
| 343 | seroval | Transitive | frontend/package-lock.json | `fromJSON()` Promise thenable assimilation (bypass GHSA-mv8w-475r-vwqw) |
| 255 | @nuxt/devtools | Transitive | frontend/package-lock.json | Unauthenticated Nuxt DevTools RPC → arbitrary command execution |
| 296 | anyio | Transitive | backend/poetry.lock | TLSStream IDNA 2003 → potential TLS certificate spoofing |
| 335 | python-jose | Direct | backend/poetry.lock | algorithm confusion guard bypassed by DER-encoded public keys |
| 164 | shell-quote | Transitive | frontend/package-lock.json | `quote()` does not escape newlines in object `.op` values |
| 230 | tar | Transitive | frontend/package-lock.json | Decompression/parse DoS via unlimited input |
| 346 | simple-git | Transitive | frontend/package-lock.json | unsafe-operation guard does not block trailer command configuration |
| 304 | PyJWT | Transitive | backend/poetry.lock | Asymmetric-PEM detection bypass (whitespace/line-ending-mutated keys) |

## High

| # | Пакет | Тип | Lockfile | Описание |
|---|-------|-----|----------|----------|
| 152 | urllib3 | Transitive | backend/poetry.lock | Decompression-bomb safeguards bypassed in streaming API |
| 308 | urllib3 | Transitive | backend/poetry.lock | `stream()`/`read_chunked()` unbounded chunk-size line buffer |
| 347 | sharp | Transitive | frontend/package-lock.json | librsvg CVE-2026-96889 |
| 277 | sharp | Transitive | frontend/package-lock.json | libheif GHSA-g89c-p67h-r497, GHSA-2jg2-4ch7-h545 |
| 191 | nuxt | Direct | frontend/package-lock.json | Route-rule middleware bypass (case-sensitivity vs routeRules) |
| 45 | python-multipart | Direct | backend/poetry.lock | Arbitrary File Write via non-default configuration |
| 149 | Mako | Transitive | backend/poetry.lock | path traversal via backslash URI on Windows (TemplateLookup) |
| 288 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Processing Instruction Target Injection |
| 286 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Element name injection via `createElement()` |
| 284 | @xmldom/xmldom | Transitive | frontend/package-lock.json | DocType `name` Injection |
| 281 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Attribute name injection via `setAttribute()` |
| 282 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Quadratic-time attribute deduplication |
| 287 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Quadratic-time parsing (malformed-input recovery) |
| 280 | @xmldom/xmldom | Transitive | frontend/package-lock.json | Quadratic-memory consumption |

## Moderate

| # | Пакет | Тип | Lockfile | Описание |
|---|-------|-----|----------|----------|
| 163 | starlette | Transitive | backend/poetry.lock | missing Host header validation poisons `request.url.path` |

## Как закрывать

1. Backend: `cd backend && poetry update <pkg>` (или bump в `pyproject.toml`) → `poetry lock` → прогнать pytest.
2. Frontend: bump родительских пакетов (`nuxt`, `@nuxt/devtools`, и т.д.) → `npm update` / `npm audit fix` → `npm run build`.
3. После мержа в основную ветку — убедиться, что алерты на GitHub стали Resolved/Dismissed.
4. Dev-only (`@nuxt/devtools`): проверить, что в prod-сборке не попадает; при необходимости исключить из prod deps.
