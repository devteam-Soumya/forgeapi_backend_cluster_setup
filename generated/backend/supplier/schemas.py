from pydantic import BaseModel

class SupplierCreate(BaseModel):
    name: str
    contactEmail: str | None = None
    phone: str | None = None
