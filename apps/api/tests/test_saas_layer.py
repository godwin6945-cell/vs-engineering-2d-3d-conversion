"""
Unit and integration tests for Phase 7: SaaS Layer
- Razorpay Subscriptions, Plans & 18% GST Invoicing
- API Keys for ERP/PLM integrations
- Outbound Webhooks with HMAC-SHA256 signatures
- Dimension Library for recurring company tolerances
- Admin Console operational metrics
"""

import pytest
from httpx import AsyncClient
from apps.api.tests.conftest import make_auth_headers


@pytest.mark.asyncio
async def test_billing_plans_list(client: AsyncClient):
    """Available plans return correct base price, 18% GST, and total in INR."""
    res = await client.get("/api/v1/billing/plans")
    assert res.status_code == 200
    plans = res.json()
    assert len(plans) == 3

    starter = next(p for p in plans if p["tier"] == "starter")
    assert starter["price_inr"] == 24999.0
    assert starter["gst_rate"] == 0.18
    assert starter["total_price_inr"] == 24999.0 * 1.18


@pytest.mark.asyncio
async def test_billing_subscription_and_order(
    client: AsyncClient,
    seeded_data: dict,
):
    """Retrieve current subscription and generate Razorpay order."""
    owner = seeded_data["owner_alpha"]

    sub_res = await client.get(
        "/api/v1/billing/subscription",
        headers=make_auth_headers(owner),
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["status"] == "active"

    order_res = await client.post(
        "/api/v1/billing/create-order",
        json={"plan_tier": "professional"},
        headers=make_auth_headers(owner),
    )
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert "order_" in order_data["order_id"]
    assert order_data["currency"] == "INR"


@pytest.mark.asyncio
async def test_billing_verify_payment_and_invoice(
    client: AsyncClient,
    seeded_data: dict,
):
    """Verifying payment upgrades plan and issues a GST invoice."""
    owner = seeded_data["owner_alpha"]

    pay_res = await client.post(
        "/api/v1/billing/verify-payment",
        json={
            "plan_tier": "enterprise",
            "razorpay_order_id": "order_test_12345",
            "razorpay_payment_id": "pay_test_98765",
            "razorpay_signature": "mock_signature_test",
        },
        headers=make_auth_headers(owner),
    )
    assert pay_res.status_code == 200
    sub_data = pay_res.json()
    assert sub_data["plan_tier"] == "enterprise"
    assert sub_data["monthly_job_limit"] == 1500

    # Verify GST invoice generated
    inv_res = await client.get(
        "/api/v1/billing/invoices",
        headers=make_auth_headers(owner),
    )
    assert inv_res.status_code == 200
    invoices = inv_res.json()
    assert len(invoices) >= 1
    assert invoices[0]["hsn_sac_code"] == "998314"
    assert invoices[0]["status"] == "paid"


@pytest.mark.asyncio
async def test_billing_update_gstin(
    client: AsyncClient,
    seeded_data: dict,
):
    """Save 15-character GSTIN for B2B tax compliance."""
    owner = seeded_data["owner_alpha"]

    res = await client.post(
        "/api/v1/billing/update-gstin",
        json={
            "gstin": "29AABCU9603R1ZM",
            "legal_business_name": "Alpha Precision Works Pvt Ltd",
            "billing_address": "Plot 42, Peenya Industrial Area, Bengaluru, Karnataka 560058",
            "billing_state_code": "29",
        },
        headers=make_auth_headers(owner),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["gstin"] == "29AABCU9603R1ZM"
    assert body["legal_business_name"] == "Alpha Precision Works Pvt Ltd"


@pytest.mark.asyncio
async def test_api_keys_create_and_list(
    client: AsyncClient,
    seeded_data: dict,
):
    """Create API key with secret token and list active keys."""
    owner = seeded_data["owner_alpha"]

    create_res = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "Siemens Teamcenter ERP Connector",
            "permissions": ["job:create", "job:read"],
        },
        headers=make_auth_headers(owner),
    )
    assert create_res.status_code == 201
    key_data = create_res.json()
    assert key_data["secret_key"].startswith("sk2s_live_")
    assert key_data["key_prefix"].startswith("sk2s_")

    list_res = await client.get(
        "/api/v1/api-keys",
        headers=make_auth_headers(owner),
    )
    assert list_res.status_code == 200
    keys = list_res.json()
    assert len(keys) >= 1
    assert any(k["name"] == "Siemens Teamcenter ERP Connector" for k in keys)


@pytest.mark.asyncio
async def test_webhooks_create_and_test(
    client: AsyncClient,
    seeded_data: dict,
):
    """Register webhook endpoint and verify HMAC-SHA256 signature dispatch."""
    owner = seeded_data["owner_alpha"]

    create_res = await client.post(
        "/api/v1/webhooks",
        json={
            "url": "https://erp.alphamachining.com/webhooks/sketch2step",
            "description": "ERP Production Dispatcher",
            "events": ["job.validated", "job.signed_off"],
        },
        headers=make_auth_headers(owner),
    )
    assert create_res.status_code == 201
    wh_data = create_res.json()
    assert wh_data["secret"].startswith("whsec_")

    # Test delivery
    test_res = await client.post(
        f"/api/v1/webhooks/{wh_data['id']}/test",
        headers=make_auth_headers(owner),
    )
    assert test_res.status_code == 200
    test_data = test_res.json()
    assert test_data["delivered"] is True
    assert test_data["signature"].startswith("sha256=")


@pytest.mark.asyncio
async def test_dimension_library_crud(
    client: AsyncClient,
    seeded_data: dict,
):
    """Add and list recurring company dimension standards."""
    owner = seeded_data["owner_alpha"]

    create_res = await client.post(
        "/api/v1/dimension-library",
        json={
            "category": "hole",
            "name": "Standard Dowel Pin Bore Ø10 H7",
            "standard_value": 10.0,
            "tolerance_plus": 0.015,
            "tolerance_minus": 0.0,
            "unit": "mm",
            "notes": "Standard dowel pin reamed bore for fixture plates",
        },
        headers=make_auth_headers(owner),
    )
    assert create_res.status_code == 201
    item = create_res.json()
    assert item["name"] == "Standard Dowel Pin Bore Ø10 H7"

    list_res = await client.get(
        "/api/v1/dimension-library?category=hole",
        headers=make_auth_headers(owner),
    )
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1


@pytest.mark.asyncio
async def test_admin_metrics(
    client: AsyncClient,
    seeded_data: dict,
):
    """Admin console aggregates usage, seats, and estimated Claude token costs."""
    owner = seeded_data["owner_alpha"]

    res = await client.get(
        "/api/v1/admin/metrics",
        headers=make_auth_headers(owner),
    )
    assert res.status_code == 200
    metrics = res.json()
    assert "total_jobs" in metrics
    assert "monthly_job_limit" in metrics
    assert "seat_limit" in metrics
    assert "estimated_claude_tokens_used" in metrics
    assert "estimated_ai_cost_inr" in metrics
