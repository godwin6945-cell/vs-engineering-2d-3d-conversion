"""
FastAPI authentication and RBAC dependency injectors.
"""

from typing import Callable, List
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sketch2step_spec.enums import OrganizationRole
from apps.api.database import get_db, set_tenant_context
from apps.api.models.user import User
from apps.api.auth.security import decode_access_token
from apps.api.auth.rbac import Permission, has_permission

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract, decode and authenticate the current user from Bearer JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        if not user_id or not org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing user or organization identity",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account does not exist or has been disabled",
        )

    # Automatically set tenant context for row-level security on this connection
    await set_tenant_context(db, user.org_id)
    return user


def require_role(allowed_roles: List[OrganizationRole]) -> Callable:
    """Dependency factory checking that user holds at least one of the specified roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = OrganizationRole(current_user.role)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return current_user

    return role_checker


def require_permission(permission: Permission) -> Callable:
    """Dependency factory checking that user's role has the designated RBAC permission."""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Missing required permission: {permission.value}",
            )
        return current_user

    return permission_checker
