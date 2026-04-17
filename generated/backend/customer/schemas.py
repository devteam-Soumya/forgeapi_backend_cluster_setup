from pydantic import BaseModel

class CustomerCreate(BaseModel):
    name: str
    email: str
