from pydantic import BaseModel

class OrderCreate(BaseModel):
    orderNumber: str
    total: float
    status: str
