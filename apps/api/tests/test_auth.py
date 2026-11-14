"""
Tests for authentication, registration, JWT validation and user info.
"""

import pytest
from httpx import AsyncClient
from apps.api.tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_register_new_tenant(client: AsyncClient):
    payload = {
        "org_name": "Zenith CNC Works",
        "org_slug": "zenith-cnc",
        "email": "lead@zenith.com",
        "full_name": "Zenith Lead",
        "password": "SecurePassword123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "lead@zenith.com"
    assert data["user"]["role"] == "OWNER"
    assert data["organization"]["slug"] == "zenith-cnc"


@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient, seeded_data: dict):
    payload = {
        "org_name": "Alpha Duplicate",
        "org_slug": "alpha-machining",  # already exists in seeded data
        "email": "new@alpha.com",
        "full_name": "New Alpha",
        "password": "Password123!",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success_and_failure(client: AsyncClient, seeded_data: dict):
    # Valid credentials
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "engineer@alpha.com", "password": "AlphaPass123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Invalid password
    bad_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "engineer@alpha.com", "password": "WrongPassword!"},
    )
    assert bad_response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_endpoint(client: AsyncClient, seeded_data: dict):
    headers = make_auth_headers(seeded_data["engineer_alpha"])
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "engineer@alpha.com"
    assert response.json()["role"] == "ENGINEER"
