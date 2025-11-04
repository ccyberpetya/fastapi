from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate
from typing import Optional, List
from fastapi import HTTPException


async def create_advertisement(db: AsyncSession, advertisement: AdvertisementCreate):
    try:
        db_advertisement = Advertisement(
            title=advertisement.title,  #
            description=advertisement.description,
            price=advertisement.price,
            author=advertisement.author
        )
        db.add(db_advertisement)
        await db.commit()
        await db.refresh(db_advertisement)
        return db_advertisement
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка целостности данных")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


async def get_advertisement(db: AsyncSession, advertisement_id: int):
    try:
        result = await db.execute(select(Advertisement).where(Advertisement.id == advertisement_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


async def update_advertisement(db: AsyncSession, advertisement_id: int, advertisement: AdvertisementUpdate):
    try:
        result = await db.execute(select(Advertisement).where(Advertisement.id == advertisement_id))
        db_advertisement = result.scalar_one_or_none()

        if not db_advertisement:
            return None

        update_data = advertisement.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_advertisement, field, value)

        await db.commit()
        await db.refresh(db_advertisement)
        return db_advertisement
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка целостности данных")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


async def delete_advertisement(db: AsyncSession, advertisement_id: int):
    try:
        result = await db.execute(select(Advertisement).where(Advertisement.id == advertisement_id))
        db_advertisement = result.scalar_one_or_none()

        if not db_advertisement:
            return False

        await db.delete(db_advertisement)
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")


async def search_advertisements(
        db: AsyncSession,
        title: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
):
    try:
        query = select(Advertisement)

        filters = []
        if title:
            filters.append(Advertisement.title.ilike(f"%{title}%"))
        if description:
            filters.append(Advertisement.description.ilike(f"%{description}%"))
        if author:
            filters.append(Advertisement.author.ilike(f"%{author}%"))
        if min_price is not None:
            filters.append(Advertisement.price >= min_price)
        if max_price is not None:
            filters.append(Advertisement.price <= max_price)

        if filters:
            query = query.where(and_(*filters))

        query = query.offset(skip).limit(limit).order_by(Advertisement.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {str(e)}")