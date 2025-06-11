from pydantic import BaseModel
from typing import List

class LocationItem(BaseModel):
    label: str
    value: str

class LocationResponse(BaseModel):
    data: List[LocationItem] 