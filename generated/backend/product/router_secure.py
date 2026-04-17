from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_product, list_products, get_product
from .schemas import ProductCreate
from generated.backend.core.rbac_dependencies import require_permission

router = APIRouter(prefix="/products", tags=["product"])


@router.post("/")
def create_item_rbac(payload: ProductCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("create_product"))):
    return create_product(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_rbac(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_product"))):
    return list_products(x_tenant_id)


@router.get("/{id}")
def get_item_rbac(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_product"))):
    item = get_product(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="product not found")
    return item

