"""
SQLAlchemy 2 async database engine and multi-tenant session management.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text
from .config import settings

# Engine configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields a standard database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def set_tenant_context(session: AsyncSession, org_id: str) -> None:
    """
    Sets the current tenant ID in PostgreSQL session variable for Row-Level Security (RLS).
    PostgreSQL policies evaluate: current_setting('app.current_org_id', true)
    """
    if settings.ENFORCE_RLS and org_id:
        # SQLite in test mode does not support SET LOCAL, so check dialect
        dialect_name = session.bind.dialect.name if session.bind else ""
        if dialect_name == "postgresql":
            await session.execute(
                text("SET LOCAL app.current_org_id = :org_id"),
                {"org_id": org_id}
            )


@asynccontextmanager
async def get_tenant_session(org_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Context manager for worker/internal jobs requiring tenant isolation context."""
    async with AsyncSessionLocal() as session:
        try:
            await set_tenant_context(session, org_id)
            yield session
        finally:
            await session.close()
