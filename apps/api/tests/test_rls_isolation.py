"""
Tenant Isolation & Row-Level Security Tests.
Proves that cross-tenant access strictly fails across all endpoints and queries.
"""

import pytest
from httpx import AsyncClient
from apps.api.tests.conftest import make_auth_headers
from apps.api.models import Job, AuditLog
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_cross_tenant_job_isolation(
    client: AsyncClient, seeded_data: dict, test_db: AsyncSession
):
    alpha_headers = make_auth_headers(seeded_data["engineer_alpha"])
    beta_headers = make_auth_headers(seeded_data["engineer_beta"])

    # 1. Org Alpha creates a proprietary aerospace drawing job
    alpha_job_res = await client.post(
        "/api/v1/jobs",
        json={
            "title": "Proprietary Alpha Turbine Flange",
            "drawing_file_url": "s3://alpha-vault/flange_v1.pdf",
        },
        headers=alpha_headers,
    )
    assert alpha_job_res.status_code == 201
    alpha_job_id = alpha_job_res.json()["id"]

    # 2. Org Beta tries to retrieve Alpha's job -> MUST return 404 (zero leakage)
    beta_get_res = await client.get(
        f"/api/v1/jobs/{alpha_job_id}",
        headers=beta_headers,
    )
    assert beta_get_res.status_code == 404
    assert "not found" in beta_get_res.json()["detail"].lower()

    # 3. Org Beta lists jobs -> Alpha's job must NOT appear in the list
    beta_list_res = await client.get("/api/v1/jobs", headers=beta_headers)
    assert beta_list_res.status_code == 200
    beta_jobs = beta_list_res.json()
    job_ids = [j["id"] for j in beta_jobs]
    assert alpha_job_id not in job_ids

    # 4. Org Beta attempts to modify dimensions on Alpha's job -> MUST return 404
    beta_patch_res = await client.patch(
        f"/api/v1/jobs/{alpha_job_id}/dimensions/dim_01",
        json={"value": 150.0},
        headers=beta_headers,
    )
    assert beta_patch_res.status_code == 404

    # 5. Org Beta Reviewer (with JOB_APPROVE permission) attempts to sign off Alpha's job -> MUST return 404
    beta_reviewer_headers = make_auth_headers(seeded_data["reviewer_beta"])
    beta_signoff_res = await client.post(
        f"/api/v1/jobs/{alpha_job_id}/sign-off",
        json={"notes": "Cross-tenant signoff attempt"},
        headers=beta_reviewer_headers,
    )
    assert beta_signoff_res.status_code == 404


@pytest.mark.asyncio
async def test_cross_tenant_audit_log_isolation(client: AsyncClient, seeded_data: dict):
    alpha_headers = make_auth_headers(seeded_data["owner_alpha"])
    beta_headers = make_auth_headers(seeded_data["engineer_beta"])

    # Alpha performs an action generating an audit entry
    await client.post(
        "/api/v1/jobs",
        json={
            "title": "Alpha Confidential Bracket",
            "drawing_file_url": "s3://alpha/confidential.dxf",
        },
        headers=alpha_headers,
    )

    # Beta attempts to read audit logs
    # Note: Beta is ENGINEER role, which doesn't have AUDIT_VIEW permission, so 403
    beta_audit_res = await client.get("/api/v1/audit-logs", headers=beta_headers)
    assert beta_audit_res.status_code == 403

    # Alpha Owner reads audit logs -> Sees own logs with org_id == org_alpha_id
    alpha_audit_res = await client.get("/api/v1/audit-logs", headers=alpha_headers)
    assert alpha_audit_res.status_code == 200
    logs = alpha_audit_res.json()
    assert len(logs) > 0
    for l in logs:
        assert l["org_id"] == seeded_data["org_alpha"].id
