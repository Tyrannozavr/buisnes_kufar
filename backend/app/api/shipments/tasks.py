import asyncio
from datetime import datetime

from sqlalchemy import delete

from app.api.shipments.models import ShipmentRequest
from app.celery_app import celery_app
from app.db.base import AsyncSessionLocal
from app_logging.logger import logger


async def purge_expired_requests() -> int:
	"""Delete expired open requests. Never touch accepted — shipments depend on them (RESTRICT)."""
	async with AsyncSessionLocal() as session:
		result = await session.execute(
			delete(ShipmentRequest).where(
				ShipmentRequest.expires_at < datetime.utcnow(),
				ShipmentRequest.status.in_(["passive", "active", "expired"]),
			)
		)
		await session.commit()
		deleted = result.rowcount or 0
		if deleted:
			logger.info("Purged %s expired shipment requests", deleted)
		return deleted


@celery_app.task(name="shipments.purge_expired_requests")
def purge_expired_requests_task() -> int:
	return asyncio.run(purge_expired_requests())
