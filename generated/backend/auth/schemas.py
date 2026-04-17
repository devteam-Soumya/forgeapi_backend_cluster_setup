from pydantic import BaseModel, EmailStr, Field


class Signup(BaseModel):
    tenant_id: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)


class Login(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
