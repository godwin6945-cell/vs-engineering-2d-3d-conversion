"""
Test configuration, database fixtures and authenticated clients.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from apps.api.main import app
from apps.api.database import get_db
from apps.api.models.base import Base
from apps.api.models import Organization, User
from apps.api.auth.security import create_access_token, get_password_hash
from sketch2step_spec.enums import OrganizationRole

# Test database: SQLite in-memory with StaticPool for async SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def seeded_data(test_db: AsyncSession):
    """Seed Org Alpha and Org Beta with users across multiple roles."""
    # Org Alpha
    org_alpha = Organization(id="org_alpha_id", name="Alpha Machining Ltd", slug="alpha-machining")
    # Org Beta
    org_beta = Organization(id="org_beta_id", name="Beta Precision Inc", slug="beta-precision")
    test_db.add_all([org_alpha, org_beta])
    await test_db.flush()

    # Org Alpha Users
    owner_alpha = User(
        id="user_owner_alpha",
        org_id=org_alpha.id,
        email="owner@alpha.com",
        full_name="Alpha Owner",
        hashed_password=get_password_hash("AlphaPass123!"),
        role=OrganizationRole.OWNER.value,
    )
    engineer_alpha = User(
        id="user_engineer_alpha",
        org_id=org_alpha.id,
        email="engineer@alpha.com",
        full_name="Alpha Engineer",
        hashed_password=get_password_hash("AlphaPass123!"),
        role=OrganizationRole.ENGINEER.value,
    )
    reviewer_alpha = User(
        id="user_reviewer_alpha",
        org_id=org_alpha.id,
        email="reviewer@alpha.com",
        full_name="Alpha Reviewer",
        hashed_password=get_password_hash("AlphaPass123!"),
        role=OrganizationRole.REVIEWER.value,
    )
    viewer_alpha = User(
        id="user_viewer_alpha",
        org_id=org_alpha.id,
        email="viewer@alpha.com",
        full_name="Alpha Viewer",
        hashed_password=get_password_hash("AlphaPass123!"),
        role=OrganizationRole.VIEWER.value,
    )

    # Org Beta Users
    engineer_beta = User(
        id="user_engineer_beta",
        org_id=org_beta.id,
        email="engineer@beta.com",
        full_name="Beta Engineer",
        hashed_password=get_password_hash("BetaPass123!"),
        role=OrganizationRole.ENGINEER.value,
    )
    reviewer_beta = User(
        id="user_reviewer_beta",
        org_id=org_beta.id,
        email="reviewer@beta.com",
        full_name="Beta Reviewer",
        hashed_password=get_password_hash("BetaPass123!"),
        role=OrganizationRole.REVIEWER.value,
    )

    test_db.add_all([
        owner_alpha,
        engineer_alpha,
        reviewer_alpha,
        viewer_alpha,
        engineer_beta,
        reviewer_beta,
    ])
    await test_db.commit()

    return {
        "org_alpha": org_alpha,
        "org_beta": org_beta,
        "owner_alpha": owner_alpha,
        "engineer_alpha": engineer_alpha,
        "reviewer_alpha": reviewer_alpha,
        "viewer_alpha": viewer_alpha,
        "engineer_beta": engineer_beta,
        "reviewer_beta": reviewer_beta,
    }


def make_auth_headers(user: User) -> dict:
    token = create_access_token({
        "sub": user.id,
        "org_id": user.org_id,
        "role": user.role,
    })
    return {"Authorization": f"Bearer {token}"}
