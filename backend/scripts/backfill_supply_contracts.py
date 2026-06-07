#!/usr/bin/env python3
"""
Backfill: legacy orders.supply_contracts_* → supply_contract + orders.supply_contract_id.

Использование:
  poetry run python scripts/backfill_supply_contracts.py --dry-run
  poetry run python scripts/backfill_supply_contracts.py
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime

from sqlalchemy import select

from app.db.base import AsyncSessionLocal
from app.api.purchases.models import Order, SupplyContract


async def backfill_supply_contracts(*, dry_run: bool = True) -> dict:
	stats = {
		"orders_scanned": 0,
		"orders_linked": 0,
		"contracts_created": 0,
		"contracts_reused": 0,
		"skipped_no_number": 0,
	}

	async with AsyncSessionLocal() as session:
		result = await session.execute(
			select(Order)
			.where(Order.supply_contracts_number.isnot(None))
			.where(Order.supply_contracts_number != "")
			.order_by(Order.id, Order.version)
		)
		orders = result.scalars().all()
		stats["orders_scanned"] = len(orders)

		pair_contracts: dict[tuple[int, int, str], SupplyContract] = {}

		for order in orders:
			number = (order.supply_contracts_number or "").strip()
			if not number:
				stats["skipped_no_number"] += 1
				continue

			if order.supply_contract_id:
				stats["orders_linked"] += 1
				continue

			key = (order.buyer_company_id, order.seller_company_id, number)
			entity = pair_contracts.get(key)

			if entity is None:
				existing = await session.execute(
					select(SupplyContract).where(
						SupplyContract.buyer_company_id == order.buyer_company_id,
						SupplyContract.seller_company_id == order.seller_company_id,
						SupplyContract.number == number,
					)
				)
				entity = existing.scalar_one_or_none()

			if entity is None:
				entity = SupplyContract(
					buyer_company_id=order.buyer_company_id,
					seller_company_id=order.seller_company_id,
					number=number,
					date=order.supply_contracts_date or order.created_at or datetime.utcnow(),
					terms_text="",
				)
				if not dry_run:
					session.add(entity)
					await session.flush()
				pair_contracts[key] = entity
				stats["contracts_created"] += 1
			else:
				pair_contracts[key] = entity
				stats["contracts_reused"] += 1

			if not dry_run:
				order.supply_contract_id = entity.id
			stats["orders_linked"] += 1

		if not dry_run:
			await session.commit()

	return stats


def main() -> None:
	parser = argparse.ArgumentParser(description="Backfill supply_contract entities from legacy order fields")
	parser.add_argument(
		"--dry-run",
		action="store_true",
		help="Only report changes without writing to DB",
	)
	args = parser.parse_args()
	stats = asyncio.run(backfill_supply_contracts(dry_run=args.dry_run))
	mode = "DRY-RUN" if args.dry_run else "APPLIED"
	print(f"[{mode}] backfill stats: {stats}")


if __name__ == "__main__":
	main()
