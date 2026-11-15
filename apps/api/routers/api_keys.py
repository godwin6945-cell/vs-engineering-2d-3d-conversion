"""
API Key router for programmatic ERP/PLM integrations.
Keys are generated with 'sk2s_live_' prefix and hashed with SHA-256 for secure storage.
"""

import hashlib
import secrets
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.database import get_db
from apps.api.models import ApiKey, User, AuditLog
from apps.api.auth.dependencies import require_permission
from apps.api.auth.rbac import Permission

router = APIRouter(prefix="/api-keys", tags=["API Keys & Integrations"])


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100, description="Description e.g. 'Teamcenter ERP Connector'")
    permissions: List[str] = Field(default_factory=lambda: ["job:create", "job:read", "export:download"])


class ApiKeyCreateResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    secret_key: str # Returned ONLY upon creation
    permissions: List[str]
    created_at: str


class ApiKeyResponse(BaseModel):
    id: str
    name: str
    key_prefix: str
    permissions: List[str]
    is_active: bool
    last_used_at: Optional[str] = None
    created_at: str


@router.get("", response_model=List[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """List registered API keys for the current organization."""
    res = await db.execute(
        select(ApiKey).where(ApiKey.org_id == current_user.org_id).order_by(desc(ApiKey.created_at))
    )
    keys = res.scalars().all()
    return [
        ApiKeyResponse(
            id=k.id,
            name=k.name,
            key_prefix=k.key_prefix,
            permissions=k.permissions,
            is_active=k.is_active,
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
            created_at=k.created_at.isoformat(),
        )
        for k in keys
    ]


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreateRequest,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new high-entropy API key for ERP/PLM integrations.
    Returns the secret key token ONCE.
    """
    raw_token = secrets.token_urlsafe(32)
    prefix = f"sk2s_{raw_token[:8]}"
    full_secret = f"sk2s_live_{raw_token}"
    hashed = hashlib.sha256(full_secret.encode("utf-8")).hexdigest()

    api_key = ApiKey(
        org_id=current_user.org_id,
        name=payload.name,
        key_prefix=prefix,
        hashed_key=hashed,
        permissions=payload.permissions,
        is_active=True,
    )
    db.add(api_key)

    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="api_key:create",
        target_type="api_key",
        target_id=api_key.id,
        details={"name": api_key.name, "prefix": prefix},
    ))
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreateResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=prefix,
        secret_key=full_secret,
        permissions=api_key.permissions,
        created_at=api_key.created_at.isoformat(),
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Revokes an active API key immediately."""
    res = await db.execute(
        select(ApiKey).where(ApiKey.id == key_id, ApiKey.org_id == current_user.org_id)
    )
    api_key = res.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="api_key:revoke",
        target_type="api_key",
        target_id=api_key.id,
        details={"name": api_key.name},
    ))
    await db.delete(api_key)
    await db.commit()
