"""
Application configuration using Pydantic Settings.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sketch2STEP Enterprise API"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://sketch2step_admin:sketch2step_secure_dev_pw@localhost:5432/sketch2step_db"
    DATABASE_SYNC_URL: str = "postgresql://sketch2step_admin:sketch2step_secure_dev_pw@localhost:5432/sketch2step_db"
    ENFORCE_RLS: bool = True

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO / S3
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_PUBLIC_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "sketch2step-drawings"
    S3_REGION: str = "us-east-1"
    S3_SECURE: bool = False

    # Security & Auth
    SECRET_KEY: str = "sketch2step_super_secret_development_key_change_in_production_32b"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ENCRYPTION_MASTER_KEY: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    # AI Models
    ANTHROPIC_API_KEY: str = "your-api-key-here"
    EXTRACT_MODEL: str = "claude-opus-5-5"
    CODEGEN_MODEL: str = "claude-sonnet-5-5"
    ALLOW_TENANT_BYOK: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
