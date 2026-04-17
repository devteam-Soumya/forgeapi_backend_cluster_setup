from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_inventory, list_inventories, get_inventory
from .schemas import InventoryCreate
from generated.backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/inventories", tags=["inventory"])


@router.post("/")
def create_item_auth(payload: InventoryCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return create_inventory(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_auth(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return list_inventories(x_tenant_id)


@router.get("/{id}")
def get_item_auth(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    item = get_inventory(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="inventory not found")
    return item

