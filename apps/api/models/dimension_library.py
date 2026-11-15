"""
Dimension Library entity for saving recurring company tolerances, holes, and standard parts.
"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization


class DimensionLibraryItem(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "dimension_library_items"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(50), index=True, nullable=False) # hole, thread, boss, slot, tolerance, plate_thickness
    name: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "Standard Dowel Pin Bore Ø10 H7"
    standard_value: Mapped[float] = mapped_column(Float, nullable=False)
    tolerance_plus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tolerance_minus: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), default="mm", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    organization: Mapped["Organization"] = relationship("Organization")
