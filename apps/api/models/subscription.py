"""
Subscription, Billing, and GST Invoicing models for Razorpay & enterprise billing.
"""

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TenantMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .organization import Organization


class Subscription(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "subscriptions"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    plan_tier: Mapped[str] = mapped_column(String(30), default="professional", nullable=False) # starter, professional, enterprise
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False) # active, past_due, trialing, canceled
    monthly_job_limit: Mapped[int] = mapped_column(Integer, default=350, nullable=False)
    monthly_jobs_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    seat_limit: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    current_period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Razorpay Gateway Identifiers
    razorpay_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    razorpay_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Indian GST Billing Metadata
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True) # 15-character GSTIN
    legal_business_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    billing_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    billing_state_code: Mapped[Optional[str]] = mapped_column(String(2), default="29", nullable=True) # State code for GST (e.g. 29 for Karnataka)

    organization: Mapped["Organization"] = relationship("Organization")


class Invoice(Base, UUIDMixin, TenantMixin, TimestampMixin):
    __tablename__ = "invoices"

    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False) # e.g. SK2S/2026/001
    amount_subtotal_inr: Mapped[float] = mapped_column(Float, nullable=False)
    gst_rate: Mapped[float] = mapped_column(Float, default=0.18, nullable=False) # 18% standard GST
    gst_amount_inr: Mapped[float] = mapped_column(Float, nullable=False)
    amount_total_inr: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    hsn_sac_code: Mapped[str] = mapped_column(String(10), default="998314", nullable=False) # Information technology software service
    status: Mapped[str] = mapped_column(String(30), default="paid", nullable=False) # paid, unpaid, refunded
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    invoice_pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    organization: Mapped["Organization"] = relationship("Organization")
