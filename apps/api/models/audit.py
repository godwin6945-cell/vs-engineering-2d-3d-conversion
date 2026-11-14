"""
Append-only Audit Log entity for enterprise compliance and security.
"""

from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization


class AuditLog(Base, UUIDMixin, TenantMixin, TimestampMixin):
    """
    Append-only audit trail.
    Tracks every security-sensitive and CAD-modifying action:
    upload, view, edit, approve, export, download, login, role change.
    """
    __tablename__ = "audit_logs"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "job", "dimension", "user", "org"
    target_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="audit_logs")
