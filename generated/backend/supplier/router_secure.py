from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_supplier, list_suppliers, get_supplier
from .schemas import SupplierCreate
from generated.backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/suppliers", tags=["supplier"])


@router.post("/")
def create_item_auth(payload: SupplierCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return create_supplier(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_auth(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return list_suppliers(x_tenant_id)


@router.get("/{id}")
def get_item_auth(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    item = get_supplier(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="supplier not found")
    return item

