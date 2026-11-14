"""
Role-Based Access Control (RBAC) definitions and permission checks.
"""

from enum import Enum
from typing import Set
from sketch2step_spec.enums import OrganizationRole


class Permission(str, Enum):
    # Job operations
    JOB_VIEW = "job:view"
    JOB_CREATE = "job:create"
    JOB_EDIT = "job:edit"
    JOB_GENERATE_CAD = "job:generate_cad"
    JOB_APPROVE = "job:approve"
    JOB_EXPORT = "job:export"
    JOB_DELETE = "job:delete"

    # Team & Org management
    ORG_VIEW = "org:view"
    ORG_UPDATE = "org:update"
    TEAM_MANAGE = "team:manage"
    BYOK_MANAGE = "byok:manage"
    BILLING_MANAGE = "billing:manage"
    AUDIT_VIEW = "audit:view"


# Role to permissions mapping
ROLE_PERMISSIONS: dict[OrganizationRole, Set[Permission]] = {
    OrganizationRole.OWNER: {
        Permission.JOB_VIEW,
        Permission.JOB_CREATE,
        Permission.JOB_EDIT,
        Permission.JOB_GENERATE_CAD,
        Permission.JOB_APPROVE,
        Permission.JOB_EXPORT,
        Permission.JOB_DELETE,
        Permission.ORG_VIEW,
        Permission.ORG_UPDATE,
        Permission.TEAM_MANAGE,
        Permission.BYOK_MANAGE,
        Permission.BILLING_MANAGE,
        Permission.AUDIT_VIEW,
    },
    OrganizationRole.ADMIN: {
        Permission.JOB_VIEW,
        Permission.JOB_CREATE,
        Permission.JOB_EDIT,
        Permission.JOB_GENERATE_CAD,
        Permission.JOB_APPROVE,
        Permission.JOB_EXPORT,
        Permission.JOB_DELETE,
        Permission.ORG_VIEW,
        Permission.ORG_UPDATE,
        Permission.TEAM_MANAGE,
        Permission.BYOK_MANAGE,
        Permission.AUDIT_VIEW,
    },
    OrganizationRole.ENGINEER: {
        Permission.JOB_VIEW,
        Permission.JOB_CREATE,
        Permission.JOB_EDIT,
        Permission.JOB_GENERATE_CAD,
        Permission.JOB_EXPORT,
        Permission.ORG_VIEW,
    },
    OrganizationRole.REVIEWER: {
        Permission.JOB_VIEW,
        Permission.JOB_APPROVE,  # Reviewer's key dedicated capability
        Permission.JOB_EXPORT,
        Permission.ORG_VIEW,
    },
    OrganizationRole.VIEWER: {
        Permission.JOB_VIEW,
        Permission.ORG_VIEW,
    },
}


def has_permission(role: OrganizationRole | str, permission: Permission) -> bool:
    """Check if given role possesses the specified permission."""
    if isinstance(role, str):
        try:
            role = OrganizationRole(role)
        except ValueError:
            return False
    return permission in ROLE_PERMISSIONS.get(role, set())
