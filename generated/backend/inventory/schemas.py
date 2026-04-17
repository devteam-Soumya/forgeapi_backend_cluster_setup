from pydantic import BaseModel

class InventoryCreate(BaseModel):
    sku: str
    quantity: int
