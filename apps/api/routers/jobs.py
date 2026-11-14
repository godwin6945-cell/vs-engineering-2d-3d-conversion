"""
Job pipeline and dimension verification endpoints.
"""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sketch2step_spec.enums import DimensionStatus, JobState
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec
from sketch2step_spec.job import JobResponse
from apps.api.database import get_db
from apps.api.models import Job, User, AuditLog
from apps.api.auth.dependencies import (
    get_current_user,
    require_permission,
)
from apps.api.auth.rbac import Permission

router = APIRouter(prefix="/jobs", tags=["Jobs & Pipelines"])


class JobCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    drawing_file_url: str
    project_id: Optional[str] = None


class DimensionUpdateRequest(BaseModel):
    value: float
    tol_plus: Optional[float] = None
    tol_minus: Optional[float] = None
    unit: Optional[str] = "mm"
    status: DimensionStatus = DimensionStatus.HUMAN_CONFIRMED
    notes: Optional[str] = None


class SignOffRequest(BaseModel):
    notes: Optional[str] = None


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    state: Optional[JobState] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List jobs belonging exclusively to the authenticated tenant organization."""
    query = select(Job).where(Job.org_id == current_user.org_id)
    if state:
        query = query.where(Job.state == state.value)
    query = query.order_by(desc(Job.created_at))

    res = await db.execute(query)
    jobs = res.scalars().all()
    return [JobResponse.model_validate(j) for j in jobs]


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreateRequest,
    current_user: User = Depends(require_permission(Permission.JOB_CREATE)),
    db: AsyncSession = Depends(get_db),
):
    """Create a new 2D drawing conversion job."""
    job = Job(
        org_id=current_user.org_id,
        project_id=payload.project_id,
        title=payload.title,
        drawing_file_url=payload.drawing_file_url,
        state=JobState.UPLOADED.value,
    )
    db.add(job)
    await db.flush()

    audit = AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="job:upload",
        target_type="job",
        target_id=job.id,
        details={"title": job.title, "file_url": job.drawing_file_url},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(job)
    return JobResponse.model_validate(job)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve job details with strict tenant isolation."""
    res = await db.execute(
        select(Job).where(Job.id == job_id, Job.org_id == current_user.org_id)
    )
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied",
        )
    return JobResponse.model_validate(job)


@router.patch("/{job_id}/dimensions/{dimension_id}", response_model=JobResponse)
async def update_dimension(
    job_id: str,
    dimension_id: str,
    payload: DimensionUpdateRequest,
    current_user: User = Depends(require_permission(Permission.JOB_EDIT)),
    db: AsyncSession = Depends(get_db),
):
    """
    Human-in-the-loop: confirm or enter an unverified or missing dimension.
    Enforces the Accuracy Rule: No dimension reaches the STEP file unless verified.
    """
    res = await db.execute(
        select(Job).where(Job.id == job_id, Job.org_id == current_user.org_id)
    )
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.spec:
        raise HTTPException(status_code=400, detail="Job drawing specification not yet extracted")

    # Load and update spec
    spec_dict = dict(job.spec)
    dims = spec_dict.get("dimensions", [])
    target_dim = None

    for dim in dims:
        if dim.get("id") == dimension_id:
            target_dim = dim
            dim["value"] = payload.value
            if payload.tol_plus is not None:
                dim["tol_plus"] = payload.tol_plus
            if payload.tol_minus is not None:
                dim["tol_minus"] = payload.tol_minus
            if payload.unit:
                dim["unit"] = payload.unit
            dim["status"] = payload.status.value
            dim["confirmed_by_user_id"] = current_user.id
            if payload.notes:
                dim["notes"] = payload.notes
            break

    if not target_dim:
        raise HTTPException(status_code=404, detail=f"Dimension '{dimension_id}' not found in spec")

    job.spec = spec_dict

    # Check if all dimensions are now verified
    spec_model = DrawingSpec.model_validate(spec_dict)
    if spec_model.all_dimensions_verified and job.state == JobState.NEEDS_REVIEW.value:
        job.state = JobState.CONFIRMED.value

    audit = AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="dimension:human_confirm",
        target_type="job",
        target_id=job.id,
        details={
            "dimension_id": dimension_id,
            "value": payload.value,
            "status": payload.status.value,
        },
    )
    db.add(audit)
    await db.commit()
    await db.refresh(job)
    return JobResponse.model_validate(job)


@router.post("/{job_id}/sign-off", response_model=JobResponse)
async def sign_off_job(
    job_id: str,
    payload: SignOffRequest,
    current_user: User = Depends(require_permission(Permission.JOB_APPROVE)),
    db: AsyncSession = Depends(get_db),
):
    """Sign-off and approval of verified 3D model (requires REVIEWER, ADMIN or OWNER)."""
    res = await db.execute(
        select(Job).where(Job.id == job_id, Job.org_id == current_user.org_id)
    )
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.signed_off_by_user_id = current_user.id
    job.signed_off_at = datetime.now(timezone.utc)
    job.state = JobState.SIGNED_OFF.value

    audit = AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="job:sign_off",
        target_type="job",
        target_id=job.id,
        details={"approved_by": current_user.full_name, "notes": payload.notes},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(job)
    return JobResponse.model_validate(job)
