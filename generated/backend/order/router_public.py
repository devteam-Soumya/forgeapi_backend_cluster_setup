from fastapi import APIRouter, Header, HTTPException

from .crud import create_order, list_orders, get_order
from .schemas import OrderCreate

router = APIRouter(prefix="/orders", tags=["order"])


@router.post("/")
def create_item(payload: OrderCreate, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return create_order(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items(x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return list_orders(x_tenant_id)


@router.get("/{id}")
def get_item(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    item = get_order(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="order not found")
    return item
