#!/usr/bin/env python3
"""
Полный пересбор каталога портфолио: 20 товаров + 2 услуги с корректными фото.

Источники: Wikimedia Commons (металл, крепёж) + Pexels только для арматуры.
Скрывает тестовый мусор — на первой странице только витрина.

Запуск:
  docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_portfolio_catalog_rewrite.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from sqlalchemy import select, update

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.company.models.company import Company
from app.api.products.models.product import Product, ProductType
from app.db.base import AsyncSessionLocal

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "product_images"
SELLER_SLUG = "stroymetall-plus"

# key → (filename, source). source: путь в uploads/ или http URL (Pexels)
IMAGE_FILES: dict[str, tuple[str, str]] = {
    # Wikimedia — уже скачаны в контейнере, реальные болты/гайки
    "bolt_nut": ("portfolio-src-bolt_nut.jpg", "portfolio-bolt-din933-m12x50.jpg"),
    "nuts_bolts": ("portfolio-src-nuts_bolts.jpg", "portfolio-nut-hex-din934-m12.jpg"),
    "bolt_mcad": ("portfolio-src-bolt_mcad.png", "portfolio-src-bolt_mcad.png"),
    # Wikimedia — металлопрокат
    "rebar": (
        "portfolio-src-rebar.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/b5/Rebar.JPG",
    ),
    "rusty_plate": (
        "portfolio-src-rusty_plate.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/6e/Rusty_steel_plate.jpg",
    ),
    "sheet_storage": (
        "portfolio-src-sheet_storage.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/1/1d/Film_-_The_Romance_of_Iron_and_Steel_%281938%29_-_sheet_steel_storage.jpg",
    ),
    "alu_profile_40": (
        "portfolio-src-alu-profile-40.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/5c/Strangkkp.jpg",
    ),
    "alu_profile_80": (
        "portfolio-src-alu-profile-80.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/e/ef/Extruded_aluminium_section_x3.jpg",
    ),
    "angle_iron": (
        "portfolio-src-angle_iron.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/3/34/Durasteel_pressurisation_duct_angle_iron_skeleton2.jpg",
    ),
    "steel_beams": (
        "portfolio-src-steel_beams.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/d2/Steel_beams.jpg",
    ),
    "structural_icons": (
        "portfolio-src-structural_icons.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/bb/Structural-steel-icons.jpg",
    ),
    "freight_truck": (
        "portfolio-src-freight_truck.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/e/ee/PLUS_freight_lorry%2C_Winschoten_%282019%29_01.jpg",
    ),
}

GOODS: list[dict] = [
    {
        "slug": "bolt-din933-m12x50",
        "article": "SM-BOLT-M12-50",
        "name": "Болт DIN 933 М12×50, класс 8.8, оцинк.",
        "price": 18.50,
        "unit_of_measurement": "шт",
        "image": "bolt_nut",
        "description": "Болт с полной резьбой DIN 933, класс прочности 8.8, цинковое покрытие. Для металлоконструкций, машиностроения и строительных креплений.",
        "characteristics": [
            {"name": "Стандарт", "value": "DIN 933 / ISO 4017"},
            {"name": "Резьба", "value": "М12 × 1,75"},
            {"name": "Длина", "value": "50 мм"},
            {"name": "Класс прочности", "value": "8.8"},
            {"name": "Покрытие", "value": "Цинк (оцинковка)"},
            {"name": "Материал", "value": "Сталь 45"},
            {"name": "Головка", "value": "Шестигранная"},
            {"name": "Тип резьбы", "value": "Полная, метрическая"},
            {"name": "Масса 1 шт.", "value": "≈ 0,045 кг"},
            {"name": "ОКЕИ", "value": "796 (шт)"},
            {"name": "Мин. партия", "value": "100 шт"},
            {"name": "Срок поставки", "value": "3–5 рабочих дней"},
            {"name": "Страна", "value": "Россия"},
        ],
    },
    {"slug": "bolt-din933-m16x60", "article": "SM-BOLT-M16-60", "name": "Болт DIN 933 М16×60, класс 8.8, оцинк.", "price": 32.00, "unit_of_measurement": "шт", "image": "bolt_mcad", "description": "Высокопрочный болт М16 для металлоконструкций и машиностроения."},
    {"slug": "nut-hex-din934-m12", "article": "SM-NUT-M12-8", "name": "Гайка шестигранная DIN 934 М12, класс 8", "price": 6.20, "unit_of_measurement": "шт", "image": "nuts_bolts", "description": "Гайка DIN 934, класс прочности 8, оцинкованная."},
    {"slug": "nut-hex-din934-m16", "article": "SM-NUT-M16-8", "name": "Гайка шестигранная DIN 934 М16, класс 8", "price": 11.40, "unit_of_measurement": "шт", "image": "bolt_nut", "description": "Гайка М16 для комплектации болтовых соединений."},
    {"slug": "washer-din125-m12", "article": "SM-WASH-M12", "name": "Шайба плоская DIN 125 М12, оцинк.", "price": 1.80, "unit_of_measurement": "шт", "image": "nuts_bolts", "description": "Плоская шайба увеличенного диаметра, оцинкованная."},
    {"slug": "stud-din975-m12x100", "article": "SM-STUD-M12", "name": "Шпилька DIN 975 М12×100, класс 8.8", "price": 45.00, "unit_of_measurement": "шт", "image": "bolt_mcad", "description": "Резьбовая шпилька с метрической резьбой по всей длине."},
    {"slug": "profile-alu-40x40", "article": "SM-ALU-40X40", "name": "Профиль алюминиевый 40×40 мм, 6 м", "price": 2450.00, "unit_of_measurement": "шт", "image": "alu_profile_40", "description": "Алюминиевый профиль для каркасов и конструкций."},
    {"slug": "profile-alu-80x40", "article": "SM-ALU-80X40", "name": "Профиль алюминиевый 80×40 мм, 6 м", "price": 3180.00, "unit_of_measurement": "шт", "image": "alu_profile_80", "description": "Прямоугольный алюминиевый профиль, промышленный размер."},
    {"slug": "sheet-steel-3mm", "article": "SM-SHEET-3MM", "name": "Лист г/к Ст3сп, 3 мм, 1500×6000 мм", "price": 48500.00, "unit_of_measurement": "л.", "image": "rusty_plate", "description": "Лист стальной горячекатаный, толщина 3 мм, ГОСТ 19903."},
    {"slug": "sheet-steel-5mm", "article": "SM-SHEET-5MM", "name": "Лист г/к Ст3сп, 5 мм, 1500×6000 мм", "price": 67200.00, "unit_of_measurement": "л.", "image": "sheet_storage", "description": "Лист стальной горячекатаный, толщина 5 мм."},
    {"slug": "angle-50x50x5", "article": "SM-ANGLE-50", "name": "Уголок стальной 50×50×5 мм, 6 м", "price": 4200.00, "unit_of_measurement": "шт", "image": "angle_iron", "description": "Горячекатаный уголок равнополочный, ГОСТ 8509-93."},
    {"slug": "angle-75x75x6", "article": "SM-ANGLE-75", "name": "Уголок стальной 75×75×6 мм, 6 м", "price": 6100.00, "unit_of_measurement": "шт", "image": "angle_iron", "description": "Уголок стальной для усиления металлоконструкций."},
    {"slug": "channel-10p", "article": "SM-CH-10P", "name": "Швеллер 10П, 12 м", "price": 18700.00, "unit_of_measurement": "шт", "image": "steel_beams", "description": "Стальной швеллер горячекатаный, ГОСТ 8240."},
    {"slug": "channel-12p", "article": "SM-CH-12P", "name": "Швеллер 12П, 12 м", "price": 22400.00, "unit_of_measurement": "шт", "image": "structural_icons", "description": "Швеллер 12П для несущих конструкций."},
    {"slug": "rebar-a500s-12", "article": "SM-ARM-12", "name": "Арматура А500С Ø12 мм", "price": 62.00, "unit_of_measurement": "кг", "image": "rebar", "description": "Арматурная сталь периодического профиля, ГОСТ 34028."},
    {"slug": "rebar-a500s-16", "article": "SM-ARM-16", "name": "Арматура А500С Ø16 мм", "price": 61.00, "unit_of_measurement": "кг", "image": "rebar", "description": "Арматура для железобетонных конструкций, класс А500С."},
    {"slug": "round-bar-20", "article": "SM-ROUND-20", "name": "Круг стальной 20 мм, Ст3сп, 6 м", "price": 890.00, "unit_of_measurement": "шт", "image": "steel_beams", "description": "Круг горячекатаный, сталь Ст3сп."},
    {"slug": "pipe-steel-57x3", "article": "SM-PIPE-57", "name": "Труба стальная ВГП Ø57×3,5 мм, 6 м", "price": 1450.00, "unit_of_measurement": "шт", "image": "structural_icons", "description": "Труба водогазопроводная, ГОСТ 3262."},
    {"slug": "mesh-welded-50x50", "article": "SM-MESH-50", "name": "Сетка сварная 50×50×3 мм, 2×1 м", "price": 780.00, "unit_of_measurement": "шт", "image": "rebar", "description": "Сварная арматурная сетка для армирования полов и плит."},
    {"slug": "flange-gost-12821", "article": "SM-FLANGE-100", "name": "Фланец стальной Ду100, Ру16, ГОСТ 12821", "price": 2350.00, "unit_of_measurement": "шт", "image": "bolt_nut", "description": "Плоский приварной фланец для трубопроводов."},
]

SERVICES: list[dict] = [
    {"slug": "montazh-metall", "article": "SM-SVC-MONT", "name": "Монтаж металлоконструкций", "price": 85000.00, "unit_of_measurement": "усл", "image": "steel_beams", "description": "Монтаж и сборка металлоконструкций на объекте заказчика."},
    {"slug": "delivery-moscow", "article": "SM-SVC-DEL", "name": "Доставка по Москве и МО", "price": 12000.00, "unit_of_measurement": "усл", "image": "freight_truck", "description": "Доставка металлопроката собственным транспортом."},
]

PORTFOLIO_SLUGS = {item["slug"] for item in GOODS + SERVICES}


def _ensure_file(filename: str, source: str) -> Path:
    dest = UPLOAD_DIR / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 5000:
        return dest

    if source.startswith("http"):
        print(f"  скачиваю: {source}")
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            for attempt in range(6):
                response = client.get(source, headers={"User-Agent": "TradeSynergy-Portfolio/1.0"})
                if response.status_code == 429:
                    wait = 4 * (attempt + 1)
                    print(f"    rate limit, жду {wait}s...")
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                dest.write_bytes(response.content)
                break
            else:
                response.raise_for_status()
    else:
        src = UPLOAD_DIR / source
        if not src.exists():
            # fallback: bolt_mcad из другого имени
            alt = UPLOAD_DIR / "portfolio-bolt-din933-m16x60.png"
            if source.endswith("bolt_mcad.png") and alt.exists():
                src = alt
            else:
                raise FileNotFoundError(f"Нет файла-источника: {src}")
        print(f"  копирую: {src.name} → {filename}")
        dest.write_bytes(src.read_bytes())

    print(f"  → {filename} ({dest.stat().st_size // 1024} KB)")
    return dest


def build_image_cache() -> dict[str, str]:
    cache: dict[str, str] = {}
    print("Подготовка фото:")
    for key, (filename, source) in IMAGE_FILES.items():
        _ensure_file(filename, source)
        cache[key] = f"/uploads/product_images/{filename}"
        if source.startswith("http"):
            time.sleep(3.0)
    return cache


async def hide_non_portfolio(session, seller_id: int) -> int:
    result = await session.execute(
        update(Product)
        .where(
            Product.is_deleted == False,
            Product.is_hidden == False,
            (Product.company_id != seller_id) | (~Product.slug.in_(PORTFOLIO_SLUGS)),
        )
        .values(is_hidden=True)
    )
    return result.rowcount or 0


async def upsert_product(session, company_id: int, spec: dict, product_type: ProductType) -> Product:
    product = (
        await session.execute(select(Product).where(Product.slug == spec["slug"]))
    ).scalar_one_or_none()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    payload = {
        "name": spec["name"],
        "description": spec["description"],
        "article": spec["article"],
        "type": product_type,
        "price": spec["price"],
        "unit_of_measurement": spec["unit_of_measurement"],
        "characteristics": spec.get("characteristics", []),
        "is_hidden": False,
        "is_deleted": False,
        "company_id": company_id,
        "updated_at": now,
        "created_at": now,
    }
    if product:
        for key, value in payload.items():
            setattr(product, key, value)
    else:
        product = Product(slug=spec["slug"], images=[], **payload)
        session.add(product)
        await session.flush()
    return product


async def main() -> None:
    print("=== Пересбор каталога портфолио ===\n")
    image_cache = build_image_cache()
    print()

    async with AsyncSessionLocal() as session:
        seller = (
            await session.execute(select(Company).where(Company.slug == SELLER_SLUG))
        ).scalar_one_or_none()
        if not seller:
            print(f"Компания {SELLER_SLUG} не найдена. Сначала: ensure_portfolio_demo_data.py")
            return

        hidden = await hide_non_portfolio(session, seller.id)
        print(f"Скрыто посторонних позиций: {hidden}\n")

        for label, items, ptype in (("Товары", GOODS, ProductType.GOOD), ("Услуги", SERVICES, ProductType.SERVICE)):
            print(f"{label} ({len(items)}):")
            for spec in items:
                product = await upsert_product(session, seller.id, spec, ptype)
                product.images = [image_cache[spec["image"]]]
                print(f"  ✓ {spec['name']}")
            print()

        await session.commit()

    print("--- Готово ---")
    print("http://localhost:8080/catalog/products")
    print(f"На первой странице: {len(GOODS)} товаров с фото")


if __name__ == "__main__":
    asyncio.run(main())
