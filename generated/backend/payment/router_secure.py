from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_payment, list_payments, get_payment
from .schemas import PaymentCreate
from generated.backend.core.rbac_dependencies import require_permission

router = APIRouter(prefix="/payments", tags=["payment"])


@router.post("/")
def create_item_rbac(payload: PaymentCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("create_payment"))):
    return create_payment(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_rbac(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_payment"))):
    return list_payments(x_tenant_id)


@router.get("/{id}")
def get_item_rbac(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_payment"))):
    item = get_payment(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="payment not found")
    return item

