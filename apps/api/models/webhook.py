"""
Webhook entity for outbound pipeline state notifications.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization


class WebhookEndpoint(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "webhook_endpoints"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False) # e.g. "https://erp.company.com/webhooks/cad"
    description: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    secret: Mapped[str] = mapped_column(String(128), nullable=False) # HMAC-SHA256 signature secret
    events: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False) # e.g. ["job.validated", "job.signed_off"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization: Mapped["Organization"] = relationship("Organization")


class WebhookDelivery(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "webhook_deliveries"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    endpoint_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
