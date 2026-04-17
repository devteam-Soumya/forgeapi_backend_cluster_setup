from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from .schemas import ProductCreate, ProductUpdate
from .service import ProductService
from generated.backend.core.db import get_database

router = APIRouter(prefix='/product', tags=['product'])

@router.post('/')
async def create_product(payload: ProductCreate):
    db = get_database()
    service = ProductService(db)
    return await service.create(payload.model_dump())

@router.get('/')
async def list_product():
    db = get_database()
    service = ProductService(db)
    return await service.list_all()

@router.get('/{item_id}')
async def get_product(item_id: str):
    db = get_database()
    service = ProductService(db)
    item = await service.get_one(item_id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item

@router.put('/{item_id}')
async def update_product(item_id: str, payload: ProductUpdate):
    db = get_database()
    service = ProductService(db)
    item = await service.update(item_id, payload.model_dump())
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    return item

@router.delete('/{item_id}')
async def delete_product(item_id: str):
    db = get_database()
    service = ProductService(db)
    deleted = await service.delete(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail='Item not found')
    return {'message': 'Deleted successfully'}
