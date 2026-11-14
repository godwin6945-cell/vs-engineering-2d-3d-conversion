"""
Audit log router providing tamper-evident log inspection for enterprise compliance.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api.database import get_db
from apps.api.models import AuditLog, User
from apps.api.auth.dependencies import (
    get_current_user,
    require_permission,
)
from apps.api.auth.rbac import Permission

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


class AuditLogResponse(BaseModel):
    id: str
    org_id: str
    user_id: Optional[str] = None
    action: str
    target_type: str
    target_id: Optional[str] = None
    details: Optional[dict] = None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    action: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve immutable audit logs for the current organization."""
    query = select(AuditLog).where(AuditLog.org_id == current_user.org_id)
    if action:
        query = query.where(AuditLog.action == action)
    query = query.order_by(desc(AuditLog.created_at)).limit(limit)

    res = await db.execute(query)
    logs = res.scalars().all()
    return [
        AuditLogResponse(
            id=l.id,
            org_id=l.org_id,
            user_id=l.user_id,
            action=l.action,
            target_type=l.target_type,
            target_id=l.target_id,
            details=l.details,
            created_at=l.created_at.isoformat(),
        )
        for l in logs
    ]
