"""
Job entity representing drawing-to-STEP conversion pipelines.
"""

from datetime import datetime
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sketch2step_spec.enums import JobState
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization
    from .project import Project


class Job(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "jobs"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    project_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    state: Mapped[str] = mapped_column(
        String(30),
        default=JobState.UPLOADED.value,
        index=True,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Drawing and generated artifacts URLs
    drawing_file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    step_file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cad_script_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    inspection_report_pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Structured extraction and geometry payloads
    spec: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    validation_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    visual_diff: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Sign-off tracking
    signed_off_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    signed_off_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="jobs")
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="jobs")
