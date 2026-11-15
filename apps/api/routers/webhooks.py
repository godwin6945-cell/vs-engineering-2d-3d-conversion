"""
Outbound Webhook router for dispatching pipeline state changes to enterprise endpoints.
Includes HMAC-SHA256 signature generation for target verification.
"""

import hashlib
import hmac
import secrets
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.database import get_db
from apps.api.models import WebhookEndpoint, WebhookDelivery, User, AuditLog
from apps.api.auth.dependencies import require_permission
from apps.api.auth.rbac import Permission

router = APIRouter(prefix="/webhooks", tags=["Webhooks & Notifications"])

SUPPORTED_EVENTS = [
    "job.created",
    "job.preprocessed",
    "job.needs_review",
    "job.confirmed",
    "job.validated",
    "job.signed_off",
    "job.failed",
]


class WebhookCreateRequest(BaseModel):
    url: str = Field(description="HTTPS Webhook Target URL")
    description: Optional[str] = "ERP Event Dispatcher"
    events: List[str] = Field(default_factory=lambda: ["job.validated", "job.signed_off"])


class WebhookEndpointResponse(BaseModel):
    id: str
    url: str
    description: Optional[str] = None
    secret: str # Secret returned for HMAC setup
    events: List[str]
    is_active: bool
    created_at: str


class WebhookTestResponse(BaseModel):
    delivered: bool
    status_code: int
    signature: str
    event: str


@router.get("", response_model=List[WebhookEndpointResponse])
async def list_webhooks(
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """List registered webhooks for the tenant organization."""
    res = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.org_id == current_user.org_id).order_by(desc(WebhookEndpoint.created_at))
    )
    endpoints = res.scalars().all()
    return [
        WebhookEndpointResponse(
            id=ep.id,
            url=ep.url,
            description=ep.description,
            secret=ep.secret,
            events=ep.events,
            is_active=ep.is_active,
            created_at=ep.created_at.isoformat(),
        )
        for ep in endpoints
    ]


@router.post("", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook(
    payload: WebhookCreateRequest,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Register an outbound webhook endpoint with generated HMAC-SHA256 signing secret."""
    for ev in payload.events:
        if ev not in SUPPORTED_EVENTS:
            raise HTTPException(status_code=400, detail=f"Unsupported webhook event '{ev}'")

    secret = f"whsec_{secrets.token_hex(24)}"
    endpoint = WebhookEndpoint(
        org_id=current_user.org_id,
        url=payload.url,
        description=payload.description,
        secret=secret,
        events=payload.events,
        is_active=True,
    )
    db.add(endpoint)

    db.add(AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="webhook:create",
        target_type="webhook_endpoint",
        target_id=endpoint.id,
        details={"url": endpoint.url, "events": endpoint.events},
    ))
    await db.commit()
    await db.refresh(endpoint)

    return WebhookEndpointResponse(
        id=endpoint.id,
        url=endpoint.url,
        description=endpoint.description,
        secret=endpoint.secret,
        events=endpoint.events,
        is_active=endpoint.is_active,
        created_at=endpoint.created_at.isoformat(),
    )


@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    endpoint_id: str,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Deletes a registered webhook endpoint."""
    res = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.org_id == current_user.org_id)
    )
    ep = res.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")

    await db.delete(ep)
    await db.commit()


@router.post("/{endpoint_id}/test", response_model=WebhookTestResponse)
async def test_webhook_dispatch(
    endpoint_id: str,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Simulates a test webhook delivery and returns the HMAC-SHA256 signature."""
    res = await db.execute(
        select(WebhookEndpoint).where(WebhookEndpoint.id == endpoint_id, WebhookEndpoint.org_id == current_user.org_id)
    )
    ep = res.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")

    test_payload = '{"event": "job.test_ping", "org_id": "' + current_user.org_id + '"}'
    signature = hmac.new(ep.secret.encode("utf-8"), test_payload.encode("utf-8"), hashlib.sha256).hexdigest()

    return WebhookTestResponse(
        delivered=True,
        status_code=200,
        signature=f"sha256={signature}",
        event="job.test_ping",
    )
