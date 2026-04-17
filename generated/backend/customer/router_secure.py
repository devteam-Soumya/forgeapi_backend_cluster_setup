from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_customer, list_customers, get_customer
from .schemas import CustomerCreate
from generated.backend.core.auth_dependencies import get_current_user

router = APIRouter(prefix="/customers", tags=["customer"])


@router.post("/")
def create_item_auth(payload: CustomerCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return create_customer(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_auth(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    return list_customers(x_tenant_id)


@router.get("/{id}")
def get_item_auth(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(get_current_user)):
    item = get_customer(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="customer not found")
    return item

