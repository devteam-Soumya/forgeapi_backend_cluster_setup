from fastapi import APIRouter, Header, HTTPException

from .crud import create_product, list_products, get_product
from .schemas import ProductCreate

router = APIRouter(prefix="/products", tags=["product"])


@router.post("/")
def create_item(payload: ProductCreate, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return create_product(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items(x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return list_products(x_tenant_id)


@router.get("/{id}")
def get_item(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    item = get_product(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="product not found")
    return item
