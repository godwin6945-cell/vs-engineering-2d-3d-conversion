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


@router.get("/export/csv")
async def export_audit_logs_csv(
    current_user: User = Depends(require_permission(Permission.AUDIT_VIEW)),
    db: AsyncSession = Depends(get_db),
):
    """
    Exports organization audit trail as an RFC 4180 compliant CSV stream.
    Used for enterprise governance and QA compliance audits.
    """
    import csv
    import io
    from fastapi.responses import Response

    query = (
        select(AuditLog)
        .where(AuditLog.org_id == current_user.org_id)
        .order_by(desc(AuditLog.created_at))
    )
    res = await db.execute(query)
    logs = res.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    # Header
    writer.writerow(["ID", "Timestamp (UTC)", "Actor User ID", "Action", "Target Type", "Target ID", "Details"])

    for log in logs:
        writer.writerow([
            log.id,
            log.created_at.isoformat(),
            log.user_id or "SYSTEM",
            log.action,
            log.target_type,
            log.target_id or "",
            str(log.details or {}),
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_trail_{current_user.org_id[:8]}.csv"
        },
    )
