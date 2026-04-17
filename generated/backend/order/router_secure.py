from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_order, list_orders, get_order
from .schemas import OrderCreate
from generated.backend.core.rbac_dependencies import require_permission

router = APIRouter(prefix="/orders", tags=["order"])


@router.post("/")
def create_item_rbac(payload: OrderCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("create_order"))):
    return create_order(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_rbac(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_order"))):
    return list_orders(x_tenant_id)


@router.get("/{id}")
def get_item_rbac(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_order"))):
    item = get_order(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="order not found")
    return item

