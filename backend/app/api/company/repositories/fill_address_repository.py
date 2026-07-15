from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.fill_address import CompanyFillAddress, FillAddressKind
from app.api.company.schemas.fill_address import CompanyFillAddressCreate, CompanyFillAddressUpdate


class CompanyFillAddressRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_by_id(self, address_id: int) -> Optional[CompanyFillAddress]:
		result = await self.session.execute(
			select(CompanyFillAddress).where(CompanyFillAddress.id == address_id)
		)
		return result.scalar_one_or_none()

	async def list_by_company(
		self,
		company_id: int,
		kind: Optional[FillAddressKind] = None,
	) -> Sequence[CompanyFillAddress]:
		query = select(CompanyFillAddress).where(CompanyFillAddress.company_id == company_id)
		if kind is not None:
			query = query.where(CompanyFillAddress.kind == kind)
		query = query.order_by(
			CompanyFillAddress.is_default.desc(),
			CompanyFillAddress.id.asc(),
		)
		result = await self.session.execute(query)
		return result.scalars().all()

	async def count_by_kind(self, company_id: int, kind: FillAddressKind) -> int:
		result = await self.session.execute(
			select(func.count())
			.select_from(CompanyFillAddress)
			.where(
				CompanyFillAddress.company_id == company_id,
				CompanyFillAddress.kind == kind,
			)
		)
		return int(result.scalar_one())

	async def clear_default(self, company_id: int, kind: FillAddressKind) -> None:
		await self.session.execute(
			update(CompanyFillAddress)
			.where(
				CompanyFillAddress.company_id == company_id,
				CompanyFillAddress.kind == kind,
				CompanyFillAddress.is_default.is_(True),
			)
			.values(is_default=False, updated_at=datetime.utcnow())
		)

	async def create(
		self,
		data: CompanyFillAddressCreate,
		company_id: int,
	) -> CompanyFillAddress:
		count = await self.count_by_kind(company_id, data.kind)
		is_default = True if count == 0 else bool(data.is_default)
		if is_default and count > 0:
			await self.clear_default(company_id, data.kind)

		row = CompanyFillAddress(
			company_id=company_id,
			kind=data.kind,
			address=data.address.strip(),
			is_default=is_default,
		)
		self.session.add(row)
		await self.session.commit()
		await self.session.refresh(row)
		return row

	async def update(
		self,
		address_id: int,
		data: CompanyFillAddressUpdate,
	) -> Optional[CompanyFillAddress]:
		row = await self.get_by_id(address_id)
		if not row:
			return None

		payload = data.model_dump(exclude_unset=True)
		if "address" in payload and payload["address"] is not None:
			payload["address"] = payload["address"].strip()

		make_default = payload.pop("is_default", None)
		if make_default is True:
			await self.clear_default(row.company_id, row.kind)
			payload["is_default"] = True
		elif make_default is False and row.is_default:
			# Нельзя снять default без замены, если это единственный адрес
			count = await self.count_by_kind(row.company_id, row.kind)
			if count <= 1:
				payload["is_default"] = True
			else:
				payload["is_default"] = False

		if payload:
			payload["updated_at"] = datetime.utcnow()
			await self.session.execute(
				update(CompanyFillAddress)
				.where(CompanyFillAddress.id == address_id)
				.values(**payload)
			)
			await self.session.commit()

		# Если сняли default с одного из нескольких — назначить первый оставшийся
		updated = await self.get_by_id(address_id)
		if updated and make_default is False and not updated.is_default:
			await self._ensure_one_default(updated.company_id, updated.kind)
			return await self.get_by_id(address_id)
		return updated

	async def set_default(self, address_id: int) -> Optional[CompanyFillAddress]:
		row = await self.get_by_id(address_id)
		if not row:
			return None
		await self.clear_default(row.company_id, row.kind)
		await self.session.execute(
			update(CompanyFillAddress)
			.where(CompanyFillAddress.id == address_id)
			.values(is_default=True, updated_at=datetime.utcnow())
		)
		await self.session.commit()
		return await self.get_by_id(address_id)

	async def delete(self, address_id: int) -> bool:
		row = await self.get_by_id(address_id)
		if not row:
			return False
		company_id, kind, was_default = row.company_id, row.kind, row.is_default
		await self.session.execute(
			delete(CompanyFillAddress).where(CompanyFillAddress.id == address_id)
		)
		await self.session.commit()
		if was_default:
			await self._ensure_one_default(company_id, kind)
		return True

	async def _ensure_one_default(self, company_id: int, kind: FillAddressKind) -> None:
		rows = await self.list_by_company(company_id, kind)
		if not rows:
			return
		if any(r.is_default for r in rows):
			return
		first = rows[0]
		await self.session.execute(
			update(CompanyFillAddress)
			.where(CompanyFillAddress.id == first.id)
			.values(is_default=True, updated_at=datetime.utcnow())
		)
		await self.session.commit()
