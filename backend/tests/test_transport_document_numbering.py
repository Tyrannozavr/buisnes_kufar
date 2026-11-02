"""Unit-тесты нумерации transport_document (§1.2)."""
from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete

from app.api.company.models.company import BusinessType, Company, TradeActivity
from app.api.purchases.models import TransportDocument, TransportDocumentType
from app.api.purchases.repositories.transport_document import TransportDocumentRepository
from app.db.base import AsyncSessionLocal


def _company(suffix: str, seed: int, trade: TradeActivity) -> Company:
	return Company(
		name=f"Num {suffix}",
		slug=f"num-{suffix}",
		type="ООО",
		trade_activity=trade,
		business_type=BusinessType.GOODS,
		activity_type="Торговля",
		description="t",
		inn=f"{seed:010d}",
		ogrn=f"{seed:013d}",
		kpp=f"{(seed % 10**9):09d}",
		country="Россия",
		federal_district="ЦФО",
		region="Москва",
		city="Москва",
		full_name=f"ООО Num {suffix}",
		registration_date=datetime.utcnow(),
		legal_address="a",
		production_address="b",
		phone="+79000000000",
		email=f"num-{suffix}@ex.com",
		website="https://example.com",
		is_active=True,
	)


@pytest.mark.asyncio
async def test_numbering_framework_application_order():
	suffix = uuid4().hex[:8]
	seed = 8200000000 + int(suffix[:4], 16) % 70000000
	owner_id = carrier_id = None
	try:
		async with AsyncSessionLocal() as session:
			owner = _company(f"o-{suffix}", seed, TradeActivity.SELLER)
			carrier = _company(f"c-{suffix}", seed + 1, TradeActivity.CARRIER)
			session.add_all([owner, carrier])
			await session.flush()
			owner_id, carrier_id = owner.id, carrier.id
			repo = TransportDocumentRepository(session)

			n1 = await repo.generate_next_number(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_CONTRACT,
			)
			assert n1 == "00001"

			parent = await repo.create(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_CONTRACT,
				number="00001",
				date=datetime(2026, 1, 1),
			)
			await session.flush()

			app1 = await repo.generate_next_number(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_APPLICATION,
				parent_id=parent.id,
			)
			assert app1 == "1"
			await repo.create(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_APPLICATION,
				number="1",
				date=datetime(2026, 1, 2),
				parent_id=parent.id,
			)
			await session.flush()
			app2 = await repo.generate_next_number(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_APPLICATION,
				parent_id=parent.id,
			)
			assert app2 == "2"

			order_n = await repo.generate_next_number(
				owner_company_id=owner.id,
				carrier_company_id=carrier.id,
				doc_type=TransportDocumentType.CARRIAGE_ORDER,
			)
			assert order_n == "000001"
			await session.commit()
	finally:
		if owner_id and carrier_id:
			async with AsyncSessionLocal() as session:
				await session.execute(
					delete(TransportDocument).where(
						TransportDocument.owner_company_id == owner_id
					)
				)
				await session.execute(
					delete(Company).where(Company.id.in_([owner_id, carrier_id]))
				)
				await session.commit()
