from fastapi import APIRouter, Header, HTTPException

from .crud import create_customer, list_customers, get_customer
from .schemas import CustomerCreate

router = APIRouter(prefix="/customers", tags=["customer"])


@router.post("/")
def create_item(payload: CustomerCreate, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return create_customer(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items(x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return list_customers(x_tenant_id)


@router.get("/{id}")
def get_item(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    item = get_customer(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="customer not found")
    return item
