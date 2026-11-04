#!/usr/bin/env python3
"""
Скачивает фото товаров из Unsplash и привязывает к каталогу портфолио.

Запуск:
  docker compose -f docker-compose.dev.yml exec backend poetry run python scripts/ensure_portfolio_product_images.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.api.company.models.company import Company
from app.api.products.models.product import Product
from app.db.base import AsyncSessionLocal

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "product_images"

# slug → URL (Unsplash, свободное использование)
PRODUCT_IMAGES: dict[str, str] = {
    "bolt-din933-m12x50": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=800&q=80",
    "nut-hex-m12-8": "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?w=800&q=80",
    "profile-alu-40x40": "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?w=800&q=80",
    "sheet-steel-3mm": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
    "angle-50x50x5": "https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=800&q=80",
    "channel-10p": "https://images.unsplash.com/photo-1489515217757-5fd1be406fef?w=800&q=80",
    "rebar-a500s-12": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80",
    "montazh-metall": "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&q=80",
    "delivery-moscow": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&q=80",
}


def download_image(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=30.0, follow_redirects=True) as client:
        response = client.get(url, headers={"User-Agent": "TradeSynergy-Portfolio/1.0"})
        response.raise_for_status()
        dest.write_bytes(response.content)


async def main() -> None:
    print("=== Картинки для каталога портфолио ===\n")

    async with AsyncSessionLocal() as session:
        seller = (
            await session.execute(select(Company).where(Company.slug == "stroymetall-plus"))
        ).scalar_one_or_none()
        if not seller:
            print("Компания stroymetall-plus не найдена. Сначала запустите ensure_portfolio_demo_data.py")
            return

        products = (
            await session.execute(
                select(Product).where(
                    Product.company_id == seller.id,
                    Product.slug.in_(PRODUCT_IMAGES.keys()),
                )
            )
        ).scalars().all()

        if not products:
            print("Товары портфолио не найдены. Сначала запустите ensure_portfolio_demo_data.py")
            return

        for product in products:
            url = PRODUCT_IMAGES[product.slug]
            filename = f"portfolio-{product.slug}.jpg"
            filepath = UPLOAD_DIR / filename
            image_path = f"/uploads/product_images/{filename}"

            print(f"  {product.name}")
            print(f"    скачиваю: {url}")
            download_image(url, filepath)
            product.images = [image_path]
            print(f"    сохранено: {filepath} ({filepath.stat().st_size // 1024} KB)")

        await session.commit()

    print(f"\nГотово: {len(products)} товаров с фото")
    print("Проверка: http://localhost:8080/catalog/products")


if __name__ == "__main__":
    asyncio.run(main())
