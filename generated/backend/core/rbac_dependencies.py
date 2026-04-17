from fastapi import Depends, HTTPException

from generated.backend.core.auth_dependencies import get_current_user


def require_permission(required_permission: str):
    def checker(current_user=Depends(get_current_user)):
        roles = current_user.get("roles", [])
        permissions = current_user.get("permissions", [])
        if "admin" in roles or "*" in permissions or required_permission in permissions:
            return current_user
        raise HTTPException(status_code=403, detail="Insufficient permission")
    return checker
