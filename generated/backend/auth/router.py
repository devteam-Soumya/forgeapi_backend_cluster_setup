from fastapi import APIRouter, HTTPException

from .schemas import Login, Signup
from .service import login, signup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
def signup_user(data: Signup):
    result = signup(data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/login")
def login_user(data: Login):
    result = login(data.model_dump())
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result
