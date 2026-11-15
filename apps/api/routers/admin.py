"""
Admin Console router for SaaS operational metrics, cost metering, and failed job inspection.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.database import get_db
from apps.api.models import Job, User, Subscription, AuditLog
from apps.api.auth.dependencies import require_role
from sketch2step_spec.enums import JobState, OrganizationRole

router = APIRouter(prefix="/admin", tags=["Admin Console & Operations"])


class UsageMetricsResponse(BaseModel):
    total_jobs: int
    validated_jobs: int
    failed_jobs: int
    total_users: int
    seat_limit: int
    monthly_jobs_used: int
    monthly_job_limit: int
    estimated_claude_tokens_used: int
    estimated_ai_cost_inr: float
    estimated_ai_cost_usd: float


class FailedJobDetail(BaseModel):
    id: str
    title: str
    state: str
    failure_reason: str
    created_at: str


@router.get("/metrics", response_model=UsageMetricsResponse)
async def get_admin_metrics(
    current_user: User = Depends(require_role([OrganizationRole.ADMIN, OrganizationRole.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve operational SaaS usage metrics, seat occupancy, and token cost estimates."""
    org_id = current_user.org_id

    # Count jobs by state
    jobs_count_res = await db.execute(
        select(func.count(Job.id)).where(Job.org_id == org_id)
    )
    total_jobs = jobs_count_res.scalar() or 0

    val_count_res = await db.execute(
        select(func.count(Job.id)).where(Job.org_id == org_id, Job.state.in_([JobState.VALIDATED.value, JobState.SIGNED_OFF.value, JobState.EXPORTED.value]))
    )
    validated_jobs = val_count_res.scalar() or 0

    fail_count_res = await db.execute(
        select(func.count(Job.id)).where(Job.org_id == org_id, Job.state == JobState.FAILED.value)
    )
    failed_jobs = fail_count_res.scalar() or 0

    # User seats count
    users_count_res = await db.execute(
        select(func.count(User.id)).where(User.org_id == org_id, User.is_active == True)
    )
    total_users = users_count_res.scalar() or 0

    # Subscription counters
    sub_res = await db.execute(
        select(Subscription).where(Subscription.org_id == org_id)
    )
    sub = sub_res.scalar_one_or_none()

    seat_limit = sub.seat_limit if sub else 10
    monthly_job_limit = sub.monthly_job_limit if sub else 350
    monthly_jobs_used = sub.monthly_jobs_used if sub else total_jobs

    # Claude token estimation (~12,500 tokens per drawing extraction pass)
    tokens_used = total_jobs * 25000
    cost_usd = round((tokens_used / 1000.0) * 0.015, 2)
    cost_inr = round(cost_usd * 86.5, 2)

    return UsageMetricsResponse(
        total_jobs=total_jobs,
        validated_jobs=validated_jobs,
        failed_jobs=failed_jobs,
        total_users=total_users,
        seat_limit=seat_limit,
        monthly_jobs_used=monthly_jobs_used,
        monthly_job_limit=monthly_job_limit,
        estimated_claude_tokens_used=tokens_used,
        estimated_ai_cost_inr=cost_inr,
        estimated_ai_cost_usd=cost_usd,
    )


@router.get("/failed-jobs", response_model=List[FailedJobDetail])
async def list_failed_jobs(
    current_user: User = Depends(require_role([OrganizationRole.ADMIN, OrganizationRole.OWNER])),
    db: AsyncSession = Depends(get_db),
):
    """Inspect failed jobs for root cause analysis and pipeline diagnostics."""
    res = await db.execute(
        select(Job).where(Job.org_id == current_user.org_id, Job.state == JobState.FAILED.value).order_by(Job.created_at.desc())
    )
    jobs = res.scalars().all()
    return [
        FailedJobDetail(
            id=j.id,
            title=j.title,
            state=j.state,
            failure_reason=j.failure_reason or "Unknown pipeline exception",
            created_at=j.created_at.isoformat(),
        )
        for j in jobs
    ]
