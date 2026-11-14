"""
Authentication and registration endpoints.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sketch2step_spec.enums import OrganizationRole
from sketch2step_spec.tenant import OrganizationResponse, UserResponse
from apps.api.database import get_db
from apps.api.models import Organization, User, AuditLog
from apps.api.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from apps.api.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    org_name: str
    org_slug: str
    email: EmailStr
    full_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponseData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    organization: OrganizationResponse


@router.post("/register", response_model=TokenResponseData, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new enterprise tenant organization and its initial Owner account."""
    # Check if org slug or user email already taken
    existing_org = await db.execute(
        select(Organization).where(Organization.slug == payload.org_slug.lower())
    )
    if existing_org.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Organization identifier '{payload.org_slug}' is already taken",
        )

    existing_user = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    # Create Organization
    org = Organization(
        name=payload.org_name,
        slug=payload.org_slug.lower(),
    )
    db.add(org)
    await db.flush()

    # Create Initial Owner User
    user = User(
        org_id=org.id,
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=OrganizationRole.OWNER.value,
        last_login_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.flush()

    # Audit log creation
    audit = AuditLog(
        org_id=org.id,
        user_id=user.id,
        action="organization:register",
        target_type="organization",
        target_id=org.id,
        details={"org_name": org.name, "owner_email": user.email},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(org)
    await db.refresh(user)

    token = create_access_token({
        "sub": user.id,
        "org_id": org.id,
        "role": user.role,
    })

    return TokenResponseData(
        access_token=token,
        user=UserResponse.model_validate(user),
        organization=OrganizationResponse.model_validate(org),
    )


@router.post("/login", response_model=TokenResponseData)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user with email and password, return tenant-scoped JWT token."""
    res = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = res.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact your organization administrator.",
        )

    # Fetch organization
    org_res = await db.execute(select(Organization).where(Organization.id == user.org_id))
    org = org_res.scalar_one_or_none()
    if not org or not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization subscription is inactive or suspended.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    audit = AuditLog(
        org_id=org.id,
        user_id=user.id,
        action="user:login",
        target_type="user",
        target_id=user.id,
    )
    db.add(audit)
    await db.commit()

    token = create_access_token({
        "sub": user.id,
        "org_id": org.id,
        "role": user.role,
    })

    return TokenResponseData(
        access_token=token,
        user=UserResponse.model_validate(user),
        organization=OrganizationResponse.model_validate(org),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve currently authenticated user profile."""
    return UserResponse.model_validate(current_user)
