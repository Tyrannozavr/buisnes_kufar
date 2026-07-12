# Gotenberg + Times New Roman

Образ для конвертации DOCX → PDF с корректным шрифтом **Times New Roman**.

## Почему не оригинальный TNR от Microsoft

Times New Roman — проприетарный шрифт Microsoft; его нельзя свободно положить в git.  
Вместо него в репозитории лежит **TeX Gyre Termes** (GUST Font License, свободная лицензия) — замена Times New Roman для печати и PDF.

В контейнере `fontconfig` сопоставляет запросы `Times New Roman` / `Times` с семейством `TeX Gyre Termes`, поэтому LibreOffice в Gotenberg рендерит PDF так, как ожидает шаблон `supply_contract.docx`.

## Файлы

| Файл | Назначение |
|------|------------|
| `fonts/texgyretermes-*.otf` | Regular / Bold / Italic / BoldItalic |
| `fonts/GUST-FONT-LICENSE.txt` | Лицензия GUST |
| `fonts/99-times-new-roman.conf` | Alias Times New Roman → TeX Gyre Termes |
| `Dockerfile` | Расширение `gotenberg/gotenberg:8` |

## Сборка и запуск (dev)

```bash
docker compose -f docker-compose.dev.yml build gotenberg
docker compose -f docker-compose.dev.yml up -d gotenberg
```

Проверка шрифта в контейнере:

```bash
docker compose -f docker-compose.dev.yml exec gotenberg fc-match "Times New Roman"
```

Ожидается путь к `texgyretermes-regular.otf`.
