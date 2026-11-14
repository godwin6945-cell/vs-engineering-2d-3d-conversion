"""
Organization management, team membership, and BYOK security endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sketch2step_spec.enums import OrganizationRole
from sketch2step_spec.tenant import OrganizationResponse, UserResponse
from apps.api.database import get_db
from apps.api.models import Organization, User, AuditLog
from apps.api.auth.dependencies import (
    get_current_user,
    require_permission,
    require_role,
)
from apps.api.auth.rbac import Permission
from apps.api.auth.security import encrypt_api_key, get_password_hash

router = APIRouter(prefix="/orgs", tags=["Organizations & Teams"])


class MemberCreateRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: OrganizationRole = OrganizationRole.ENGINEER


class RoleUpdateRequest(BaseModel):
    role: OrganizationRole


class UpdateOrgSettingsRequest(BaseModel):
    name: Optional[str] = None
    retention_days: Optional[int] = Field(default=None, ge=7, le=3650)
    anthropic_api_key: Optional[str] = None


@router.get("/current", response_model=OrganizationResponse)
async def get_current_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details of the user's current organization."""
    res = await db.execute(select(Organization).where(Organization.id == current_user.org_id))
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


@router.patch("/current", response_model=OrganizationResponse)
async def update_current_organization(
    payload: UpdateOrgSettingsRequest,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Update organization settings, retention policy, and BYOK Anthropic key."""
    res = await db.execute(select(Organization).where(Organization.id == current_user.org_id))
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if payload.name is not None:
        org.name = payload.name
    if payload.retention_days is not None:
        org.retention_days = payload.retention_days
    if payload.anthropic_api_key:
        org.encrypted_anthropic_api_key = encrypt_api_key(payload.anthropic_api_key)

    audit = AuditLog(
        org_id=org.id,
        user_id=current_user.id,
        action="organization:update_settings",
        target_type="organization",
        target_id=org.id,
        details={
            "retention_days": payload.retention_days,
            "has_byok": bool(payload.anthropic_api_key),
        },
    )
    db.add(audit)
    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)


@router.get("/members", response_model=List[UserResponse])
async def list_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all team members inside the current organization."""
    res = await db.execute(
        select(User).where(User.org_id == current_user.org_id).order_by(User.created_at.asc())
    )
    members = res.scalars().all()
    return [UserResponse.model_validate(m) for m in members]


@router.post("/members", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    payload: MemberCreateRequest,
    current_user: User = Depends(require_permission(Permission.TEAM_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Add a new engineer or team member to the organization."""
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    new_user = User(
        org_id=current_user.org_id,
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role.value,
    )
    db.add(new_user)
    await db.flush()

    audit = AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="team:member_add",
        target_type="user",
        target_id=new_user.id,
        details={"member_email": new_user.email, "role": new_user.role},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse.model_validate(new_user)


@router.patch("/members/{member_id}/role", response_model=UserResponse)
async def update_member_role(
    member_id: str,
    payload: RoleUpdateRequest,
    current_user: User = Depends(require_permission(Permission.TEAM_MANAGE)),
    db: AsyncSession = Depends(get_db),
):
    """Change a member's role (enforces Owner/Admin permission, prevents demoting the last Owner)."""
    res = await db.execute(
        select(User).where(User.id == member_id, User.org_id == current_user.org_id)
    )
    target_user = res.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404, detail="Member not found in organization")

    old_role = target_user.role
    target_user.role = payload.role.value

    audit = AuditLog(
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="team:role_change",
        target_type="user",
        target_id=target_user.id,
        details={"from_role": old_role, "to_role": payload.role.value},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(target_user)
    return UserResponse.model_validate(target_user)
