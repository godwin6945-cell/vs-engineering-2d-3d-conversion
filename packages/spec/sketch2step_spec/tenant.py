"""
Multi-tenant organization, user, and authentication schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from .enums import OrganizationRole


class OrganizationBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=50)
    is_active: bool = True
    retention_days: int = Field(default=90, ge=7, le=3650)
    allow_byok: bool = True


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationResponse(OrganizationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=100)
    role: OrganizationRole = OrganizationRole.ENGINEER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    org_id: Optional[str] = None


class UserResponse(UserBase):
    id: str
    org_id: str
    created_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TokenPayload(BaseModel):
    sub: str  # user_id
    org_id: str
    role: OrganizationRole
    exp: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
