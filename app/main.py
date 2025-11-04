from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List


from app.database import engine, get_db
from app import models, schemas, crud


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Advertisement Service",
    description="Сервис для размещения объявлений купли/продажи",
    version="1.0.0"
)

@app.post("/advertisement", response_model=schemas.Advertisement)
def create_advertisement(
    advertisement: schemas.AdvertisementCreate,
    db: Session = Depends(get_db)
):
    return crud.create_advertisement(db=db, advertisement=advertisement)

@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def read_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_advertisement = crud.get_advertisement(db, advertisement_id=advertisement_id)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def update_advertisement(
    advertisement_id: int,
    advertisement: schemas.AdvertisementUpdate,
    db: Session = Depends(get_db)
):
    db_advertisement = crud.update_advertisement(db, advertisement_id=advertisement_id, advertisement=advertisement)
    if db_advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement

@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    success = crud.delete_advertisement(db, advertisement_id=advertisement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Advertisement deleted successfully"}

@app.get("/advertisement", response_model=List[schemas.Advertisement])
def search_advertisements(
    headline: Optional[str] = Query(None, description="Поиск по заголовку"),
    description: Optional[str] = Query(None, description="Поиск по описанию"),
    author: Optional[str] = Query(None, description="Поиск по автору"),
    min_price: Optional[float] = Query(None, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, description="Максимальная цена"),
    skip: int = Query(0, description="Количество записей для пропуска"),
    limit: int = Query(100, description="Лимит записей"),
    db: Session = Depends(get_db)
):
    return crud.search_advertisements(
        db=db,
        headline=headline,
        description=description,
        author=author,
        min_price=min_price,
        max_price=max_price,
        skip=skip,
        limit=limit
    )

@app.get("/")
def read_root():
    return {"message": "Advertisement Service API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}