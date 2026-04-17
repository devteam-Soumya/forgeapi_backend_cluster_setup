from fastapi import APIRouter, Depends, Header, HTTPException

from .crud import create_category, list_categories, get_category
from .schemas import CategoryCreate
from generated.backend.core.rbac_dependencies import require_permission

router = APIRouter(prefix="/categories", tags=["category"])


@router.post("/")
def create_item_rbac(payload: CategoryCreate, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("create_category"))):
    return create_category(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items_rbac(x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_category"))):
    return list_categories(x_tenant_id)


@router.get("/{id}")
def get_item_rbac(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id"), current_user=Depends(require_permission("read_category"))):
    item = get_category(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="category not found")
    return item

