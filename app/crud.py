from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models import Advertisement
from app.schemas import AdvertisementCreate, AdvertisementUpdate
from typing import Optional, Dict, Any


def create_advertisement(db: Session, advertisement: AdvertisementCreate):
    db_advertisement = Advertisement(
        headline=advertisement.headline,
        description=advertisement.description,
        price=advertisement.price,
        author=advertisement.author
    )
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def get_advertisement(db: Session, advertisement_id: int):
    return db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()


def update_advertisement(db: Session, advertisement_id: int, advertisement: AdvertisementUpdate):
    db_advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if not db_advertisement:
        return None

    update_data = advertisement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_advertisement, field, value)

    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def delete_advertisement(db: Session, advertisement_id: int):
    db_advertisement = db.query(Advertisement).filter(Advertisement.id == advertisement_id).first()
    if not db_advertisement:
        return False

    db.delete(db_advertisement)
    db.commit()
    return True


def search_advertisements(
        db: Session,
        headline: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
):
    query = db.query(Advertisement)

    filters = []
    if headline:
        filters.append(Advertisement.headline.ilike(f"%{headline}%"))
    if description:
        filters.append(Advertisement.description.ilike(f"%{description}%"))
    if author:
        filters.append(Advertisement.author.ilike(f"%{author}%"))
    if min_price is not None:
        filters.append(Advertisement.price >= min_price)
    if max_price is not None:
        filters.append(Advertisement.price <= max_price)

    if filters:
        query = query.filter(and_(*filters))

    return query.offset(skip).limit(limit).all()