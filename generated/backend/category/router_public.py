from fastapi import APIRouter, Header, HTTPException

from .crud import create_category, list_categories, get_category
from .schemas import CategoryCreate

router = APIRouter(prefix="/categories", tags=["category"])


@router.post("/")
def create_item(payload: CategoryCreate, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return create_category(x_tenant_id, payload.model_dump())


@router.get("/")
def list_items(x_tenant_id: str = Header(..., alias="x-tenant-id")):
    return list_categories(x_tenant_id)


@router.get("/{id}")
def get_item(id: str, x_tenant_id: str = Header(..., alias="x-tenant-id")):
    item = get_category(x_tenant_id, id)
    if not item:
        raise HTTPException(status_code=404, detail="category not found")
    return item
