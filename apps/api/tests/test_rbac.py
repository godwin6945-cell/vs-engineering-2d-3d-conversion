"""
Role-Based Access Control (RBAC) tests.
Verifies permission boundaries for Owner, Admin, Engineer, Reviewer, and Viewer.
"""

import pytest
from httpx import AsyncClient
from apps.api.tests.conftest import make_auth_headers
from apps.api.models import Job
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_viewer_cannot_create_job(client: AsyncClient, seeded_data: dict):
    headers = make_auth_headers(seeded_data["viewer_alpha"])
    payload = {
        "title": "Drawing 001",
        "drawing_file_url": "s3://bucket/part.pdf",
    }
    response = await client.post("/api/v1/jobs", json=payload, headers=headers)
    assert response.status_code == 403
    assert "Missing required permission" in response.json()["detail"]


@pytest.mark.asyncio
async def test_engineer_can_create_job_but_cannot_sign_off(
    client: AsyncClient, seeded_data: dict, test_db: AsyncSession
):
    eng_headers = make_auth_headers(seeded_data["engineer_alpha"])

    # 1. Engineer creates job
    create_res = await client.post(
        "/api/v1/jobs",
        json={"title": "Bracket DXF", "drawing_file_url": "s3://drawings/bracket.dxf"},
        headers=eng_headers,
    )
    assert create_res.status_code == 201
    job_id = create_res.json()["id"]

    # 2. Engineer attempts sign-off -> MUST FAIL with 403 Forbidden
    signoff_res = await client.post(
        f"/api/v1/jobs/{job_id}/sign-off",
        json={"notes": "Signing off early"},
        headers=eng_headers,
    )
    assert signoff_res.status_code == 403
    assert "job:approve" in signoff_res.json()["detail"]

    # 3. Reviewer signs off -> MUST SUCCEED
    rev_headers = make_auth_headers(seeded_data["reviewer_alpha"])
    rev_res = await client.post(
        f"/api/v1/jobs/{job_id}/sign-off",
        json={"notes": "All GD&T verified by QA Lead"},
        headers=rev_headers,
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["state"] == "SIGNED_OFF"
    assert rev_res.json()["signed_off_by_user_id"] == seeded_data["reviewer_alpha"].id


@pytest.mark.asyncio
async def test_team_management_permissions(client: AsyncClient, seeded_data: dict):
    eng_headers = make_auth_headers(seeded_data["engineer_alpha"])
    owner_headers = make_auth_headers(seeded_data["owner_alpha"])

    new_member_payload = {
        "email": "new.hire@alpha.com",
        "full_name": "New Hire",
        "password": "Password123!",
        "role": "ENGINEER",
    }

    # Engineer cannot add team member
    res_eng = await client.post(
        "/api/v1/orgs/members",
        json=new_member_payload,
        headers=eng_headers,
    )
    assert res_eng.status_code == 403

    # Owner can add team member
    res_owner = await client.post(
        "/api/v1/orgs/members",
        json=new_member_payload,
        headers=owner_headers,
    )
    assert res_owner.status_code == 201
    assert res_owner.json()["email"] == "new.hire@alpha.com"
