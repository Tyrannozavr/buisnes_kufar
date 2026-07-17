from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.company.models.fleet import CompanyVehicle, CompanyDriver
from app.api.company.schemas.fleet import (
	CompanyVehicleCreate,
	CompanyVehicleUpdate,
	CompanyDriverCreate,
	CompanyDriverUpdate,
)


class CompanyVehicleRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def list_by_company(self, company_id: int) -> Sequence[CompanyVehicle]:
		result = await self.session.execute(
			select(CompanyVehicle)
			.where(CompanyVehicle.company_id == company_id)
			.order_by(CompanyVehicle.id.desc())
		)
		return result.scalars().all()

	async def get_by_id(self, vehicle_id: int) -> Optional[CompanyVehicle]:
		result = await self.session.execute(
			select(CompanyVehicle).where(CompanyVehicle.id == vehicle_id)
		)
		return result.scalar_one_or_none()

	async def create(self, data: CompanyVehicleCreate, company_id: int) -> CompanyVehicle:
		row = CompanyVehicle(company_id=company_id, **data.model_dump())
		self.session.add(row)
		await self.session.commit()
		await self.session.refresh(row)
		return row

	async def update(self, vehicle_id: int, data: CompanyVehicleUpdate) -> Optional[CompanyVehicle]:
		row = await self.get_by_id(vehicle_id)
		if not row:
			return None
		payload = data.model_dump(exclude_unset=True)
		if payload:
			payload["updated_at"] = datetime.utcnow()
			await self.session.execute(
				update(CompanyVehicle).where(CompanyVehicle.id == vehicle_id).values(**payload)
			)
			await self.session.commit()
		return await self.get_by_id(vehicle_id)

	async def delete(self, vehicle_id: int) -> bool:
		row = await self.get_by_id(vehicle_id)
		if not row:
			return False
		await self.session.execute(delete(CompanyVehicle).where(CompanyVehicle.id == vehicle_id))
		await self.session.commit()
		return True


class CompanyDriverRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def list_by_company(self, company_id: int) -> Sequence[CompanyDriver]:
		result = await self.session.execute(
			select(CompanyDriver)
			.where(CompanyDriver.company_id == company_id)
			.order_by(CompanyDriver.id.desc())
		)
		return result.scalars().all()

	async def get_by_id(self, driver_id: int) -> Optional[CompanyDriver]:
		result = await self.session.execute(
			select(CompanyDriver).where(CompanyDriver.id == driver_id)
		)
		return result.scalar_one_or_none()

	async def create(self, data: CompanyDriverCreate, company_id: int) -> CompanyDriver:
		row = CompanyDriver(company_id=company_id, **data.model_dump())
		self.session.add(row)
		await self.session.commit()
		await self.session.refresh(row)
		return row

	async def update(self, driver_id: int, data: CompanyDriverUpdate) -> Optional[CompanyDriver]:
		row = await self.get_by_id(driver_id)
		if not row:
			return None
		payload = data.model_dump(exclude_unset=True)
		if payload:
			payload["updated_at"] = datetime.utcnow()
			await self.session.execute(
				update(CompanyDriver).where(CompanyDriver.id == driver_id).values(**payload)
			)
			await self.session.commit()
		return await self.get_by_id(driver_id)

	async def delete(self, driver_id: int) -> bool:
		row = await self.get_by_id(driver_id)
		if not row:
			return False
		await self.session.execute(delete(CompanyDriver).where(CompanyDriver.id == driver_id))
		await self.session.commit()
		return True
