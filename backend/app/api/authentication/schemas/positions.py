from typing import List
from pydantic import BaseModel

from app.api.authentication.models.roles_positions import Position


class PositionResponse(BaseModel):
    """Ответ с информацией о должности"""
    value: str
    label: str


class PositionsListResponse(BaseModel):
    """Ответ со списком поддерживаемых должностей"""
    positions: List[PositionResponse]
