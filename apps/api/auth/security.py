"""
Security primitives: Password hashing, JWT token handling, and BYOK envelope encryption.
"""

import base64
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
from jose import JWTError, jwt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from apps.api.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Generate bcrypt password hash."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create signed HS256 JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise ValueError("Invalid or expired token") from e


def encrypt_api_key(plain_api_key: str) -> str:
    """
    Encrypt tenant BYOK API key using AES-256-GCM.
    Returns base64 encoded payload of nonce + ciphertext.
    """
    key_bytes = bytes.fromhex(settings.ENCRYPTION_MASTER_KEY[:64])
    aesgcm = AESGCM(key_bytes)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_api_key.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("utf-8")


def decrypt_api_key(encrypted_payload: str) -> str:
    """Decrypt tenant BYOK API key."""
    raw = base64.b64decode(encrypted_payload.encode("utf-8"))
    nonce = raw[:12]
    ciphertext = raw[12:]
    key_bytes = bytes.fromhex(settings.ENCRYPTION_MASTER_KEY[:64])
    aesgcm = AESGCM(key_bytes)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode("utf-8")
