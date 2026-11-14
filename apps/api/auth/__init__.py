"""
Auth and security module for Sketch2STEP Enterprise.
"""

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    encrypt_api_key,
    decrypt_api_key,
)
from .rbac import Permission, has_permission, ROLE_PERMISSIONS
from .dependencies import (
    get_current_user,
    require_role,
    require_permission,
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "decode_access_token",
    "encrypt_api_key",
    "decrypt_api_key",
    "Permission",
    "has_permission",
    "ROLE_PERMISSIONS",
    "get_current_user",
    "require_role",
    "require_permission",
]
