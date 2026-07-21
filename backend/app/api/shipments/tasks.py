import asyncio
from datetime import datetime

from sqlalchemy import delete

from app.api.shipments.models import ShipmentRequest
from app.celery_app import celery_app
from app.db.base import AsyncSessionLocal


async def purge_expired_requests() -> int:
	"""Delete requests older than their 14-day expiry; callable directly in tests."""
	async with AsyncSessionLocal() as session:
		result = await session.execute(
			delete(ShipmentRequest).where(ShipmentRequest.expires_at < datetime.utcnow())
		)
		await session.commit()
		return result.rowcount or 0


@celery_app.task(name="shipments.purge_expired_requests")
def purge_expired_requests_task() -> int:
	return asyncio.run(purge_expired_requests())
