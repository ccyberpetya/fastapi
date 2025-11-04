from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import asyncio

from app.database import engine, get_db
from app import models, schemas, crud

app = FastAPI(
    title="Advertisement Service",
    description="Сервис для размещения объявлений купли/продажи",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы при запуске
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.post("/advertisement", response_model=schemas.Advertisement)
async def create_advertisement(
    advertisement: schemas.AdvertisementCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_advertisement(db=db, advertisement=advertisement)

@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def read_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    db_advertisement = await crud.get_advertisement(db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
async def update_advertisement(
    advertisement_id: int,
    advertisement: schemas.AdvertisementUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_advertisement = await crud.update_advertisement(db, advertisement_id=advertisement_id, advertisement=advertisement)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud.delete_advertisement(db, advertisement_id=advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Advertisement deleted successfully"}

@app.get("/advertisement", response_model=List[schemas.Advertisement])
async def search_advertisements(
    title: Optional[str] = Query(None, description="Поиск по заголовку"),  #
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    skip: int = Query(0, description="Количество записей для пропуска"),
    limit: int = Query(100, le=100, description="Лимит записей (максимум 100)"),
    db: AsyncSession = Depends(get_db)
):
    return await crud.search_advertisements(
        db=db,
        title=title,
        description=description,
        author=author,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )

@app.get("/")
async def read_root():
    return {"message": "Advertisement Service API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}