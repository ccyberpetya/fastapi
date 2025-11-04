from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class AdvertisementBase(BaseModel):
    headline: str
    description: str
    price: Decimal
    author: str


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    headline: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    author: Optional[str] = None


class Advertisement(AdvertisementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime