"""
Unit and integration tests for Sign-off, Versioning, and Audit CSV Export.
"""

import csv
import io
import pytest
from httpx import AsyncClient
from sketch2step_spec.enums import JobState
from apps.api.models import Job
from apps.api.tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_sign_off_gating_and_success(
    client: AsyncClient,
    test_db,
    seeded_data: dict,
):
    """Sign-off requires JOB_APPROVE (Reviewer passes, Engineer fails)."""
    org_alpha = seeded_data["org_alpha"]
    reviewer = seeded_data["reviewer_alpha"]
    engineer = seeded_data["engineer_alpha"]

    # Create job in test_db
    job = Job(
        org_id=org_alpha.id,
        title="Flange Mount",
        drawing_file_url="flange.png",
        state=JobState.VALIDATED.value,
        version=1,
    )
    test_db.add(job)
    await test_db.commit()
    await test_db.refresh(job)

    # Engineer fails with 403
    eng_res = await client.post(
        f"/api/v1/jobs/{job.id}/sign-off",
        json={"notes": "Looks good"},
        headers=make_auth_headers(engineer),
    )
    assert eng_res.status_code == 403

    # Reviewer succeeds with 200
    rev_res = await client.post(
        f"/api/v1/jobs/{job.id}/sign-off",
        json={"notes": "Approved for CNC milling"},
        headers=make_auth_headers(reviewer),
    )
    assert rev_res.status_code == 200
    body = rev_res.json()
    assert body["state"] == JobState.SIGNED_OFF.value
    assert body["signed_off_by_user_id"] == reviewer.id


@pytest.mark.asyncio
async def test_fork_job_version(
    client: AsyncClient,
    test_db,
    seeded_data: dict,
):
    """Forking a job increments version (v1 -> v2) and creates a new linked job."""
    org_alpha = seeded_data["org_alpha"]
    owner = seeded_data["owner_alpha"]

    job = Job(
        org_id=org_alpha.id,
        title="Shaft Housing",
        drawing_file_url="shaft.png",
        state=JobState.SIGNED_OFF.value,
        version=1,
        spec={"drawing_number": "DWG-01", "dimensions": [{"id": "d1", "name": "L", "value": 100.0, "unit": "mm", "tol_plus": 0.1, "tol_minus": 0.1, "type": "linear", "source": "printed", "confidence": 1.0, "view": "front", "status": "verified_auto"}]},
    )
    test_db.add(job)
    await test_db.commit()
    await test_db.refresh(job)

    fork_res = await client.post(
        f"/api/v1/jobs/{job.id}/fork-version",
        json={
            "title_suffix": "Rev 2",
            "dimension_updates": [{"id": "d1", "value": 125.0}],
        },
        headers=make_auth_headers(owner),
    )
    assert fork_res.status_code == 201
    forked_job = fork_res.json()
    assert forked_job["version"] == 2
    assert "Rev 2" in forked_job["title"]
    assert forked_job["spec"]["dimensions"][0]["value"] == 125.0


@pytest.mark.asyncio
async def test_audit_logs_csv_export(
    client: AsyncClient,
    seeded_data: dict,
):
    """Audit logs export as standard RFC 4180 CSV."""
    owner = seeded_data["owner_alpha"]

    res = await client.get(
        "/api/v1/audit-logs/export/csv",
        headers=make_auth_headers(owner),
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]

    csv_text = res.text
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    assert len(rows) >= 1
    headers = rows[0]
    assert "Timestamp (UTC)" in headers
    assert "Action" in headers
    assert "Target Type" in headers
