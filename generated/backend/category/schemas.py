from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    slug: str
    isActive: bool
