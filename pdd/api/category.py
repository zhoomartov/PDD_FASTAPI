from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from pdd.db.models import Category
from pdd.db.schema import CategorySchema
from pdd.db.database import SessionLocal
from typing import List
from sqlalchemy.orm import Session


category_router = APIRouter(prefix="/category", tags=["Category"])

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@category_router.post( "/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
def create_category(category: CategorySchema, db: Session = Depends(get_db)):
    db_category = Category(category_name=category.category_name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@category_router.get('/', response_model=List[CategorySchema])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@category_router.get('/{category_id}/', response_model=CategorySchema)
def get_categories(category_id: int, db: Session = Depends(get_db)):
    db_categories = db.query(Category).filter(Category.id == category_id).first()
    if db_categories is None:
        raise HTTPException(status_code=404, detail='Category Not Found')
    return db_categories

@category_router.put('/{category_id}/', response_model=dict)
def update_categories(category_id: int, category: CategorySchema, db: Session = Depends(get_db)):
    db_categories = db.query(Category).filter(Category.id == category_id).first()
    if db_categories is None:
        raise HTTPException(status_code=404, detail='Category Not Found')
    db_categories.category_name = category.category_name
    db.commit()
    return {'message': 'Updated'}

@category_router.delete('/{category_id}/', response_model=dict)
def delete_categories(category_id: int, db: Session = Depends(get_db)):
    db_categories = db.query(Category).filter(Category.id == category_id).first()
    if db_categories is None:
        raise HTTPException(status_code=404, detail='Category Not Found')
    db.delete(db_categories)
    db.commit()
    return {'message': 'Deleted'}