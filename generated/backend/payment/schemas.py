from pydantic import BaseModel

class PaymentCreate(BaseModel):
    transactionId: str
    amount: float
    status: str
