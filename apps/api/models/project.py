"""
Project / Folder model for grouping jobs within an organization.
"""

from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization
    from .job import Job


class Project(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "projects"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), default="", nullable=False)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="projects")
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="project")
