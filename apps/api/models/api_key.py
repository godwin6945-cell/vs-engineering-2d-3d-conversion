"""
API Key entity for enterprise programmatic access (ERP/PLM integrations).
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization


class ApiKey(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "api_keys"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "Siemens Teamcenter Connector"
    key_prefix: Mapped[str] = mapped_column(String(16), index=True, nullable=False) # e.g. "sk2s_live_a1b2"
    hashed_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False) # SHA-256 hash of secret
    permissions: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization")
