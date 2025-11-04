from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional
import re

class AdvertisementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Заголовок объявления")
    description: str = Field(..., min_length=1, description="Описание объявления")
    price: float = Field(..., gt=0, description="Цена")  #
    author: str = Field(..., min_length=1, max_length=100, description="Автор объявления")

    @field_validator('title', 'author')
    @classmethod
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Поле не может быть пустым')
        return v.strip()

    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Цена должна быть положительной')
        if v > 99999999.99:
            raise ValueError('Цена слишком большая')
        return v


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, gt=0)
    author: Optional[str] = Field(None, min_length=1, max_length=100)


class Advertisement(AdvertisementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime