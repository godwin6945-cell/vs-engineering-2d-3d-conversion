# Sketch2STEP Enterprise — REST API Reference

Base URL: `http://localhost:8000/api/v1`  
Authentication: Bearer JWT Token (`Authorization: Bearer <jwt>`) or API Key (`X-API-Key: sk2s_live_...`)

---

## 1. Authentication & Organization

### `POST /auth/login`
Authenticates a user and returns a scoped JWT bearer token.

**Request:**
```json
{
  "email": "engineer@precisionmachining.com",
  "password": "secure_password_123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "tenant_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "role": "LEAD_ENGINEER"
}
```

---

## 2. Jobs & Conversion Pipelines

### `POST /jobs`
Uploads a 2D drawing (PDF, DXF, PNG, JPG) and initializes the multi-pass extraction pipeline.

**Request:** `multipart/form-data`
- `file`: Binary file stream
- `title`: "Flange Adapter Housing"
- `drawing_number`: "DWG-2026-FLG-04"
- `general_tolerance`: "ISO 2768-m"

**Response (201 Created):**
```json
{
  "job_id": "job_3a8b9c",
  "status": "UPLOADED",
  "created_at": "2026-11-15T10:00:00Z"
}
```

### `GET /jobs/{id}`
Returns complete job state, drawing metadata, and pipeline stage.

### `GET /jobs/{id}/spec`
Retrieves the confirmed `DrawingSpec`, including all dimensions, tolerances, bounding boxes, and 3-pass agreement evidence.

---

## 3. Review & Confirmation

### `POST /jobs/{id}/confirm-dimension`
Confirms or manually overrides an unverified dimension. Required to unblock CAD generation.

**Request:**
```json
{
  "dimension_id": "dim_04",
  "confirmed_value": 24.0,
  "tol_plus": 0.1,
  "tol_minus": 0.1,
  "notes": "Verified from section B-B callout"
}
```

---

## 4. CAD Compilation & Validation

### `POST /jobs/{id}/compile`
Triggers deterministic feature compilation. Blocked with `400 Bad Request` if any dimension remains unverified.

### `GET /jobs/{id}/validation`
Returns OpenCascade physical geometry measurement metrics:
```json
{
  "is_valid_solid": true,
  "is_shell_closed": true,
  "volume_mm3": 182001.9,
  "surface_area_mm2": 24150.3,
  "bounding_box": "125.0 x 125.0 x 18.0 mm",
  "measurements": [
    {
      "name": "Pitch Circle Diameter",
      "specified": 95.0,
      "measured": 95.0,
      "tolerance": "+0.15 / -0.15",
      "deviation": 0.0,
      "result": "PASS"
    }
  ]
}
```

---

## 5. QA Sign-Off & Exports

### `POST /jobs/{id}/sign-off`
Role-gated sign-off. Requires `LEAD_ENGINEER` or `ADMIN`.

**Request:**
```json
{
  "inspector_notes": "All dimensions physically verified against ISO 2768-m standards."
}
```

### `GET /jobs/{id}/export/step`
Downloads the certified ISO 10303-21 STEP CAD model (`.step`).

### `GET /jobs/{id}/export/report`
Downloads the formal ISO 9001 QA Inspection Certificate (`.pdf`).

---

## 6. SaaS Layer: Billing, API Keys & Webhooks

### `POST /billing/subscription`
Initiates a Razorpay subscription with 18% Indian GST.

**Request:**
```json
{
  "plan_tier": "PROFESSIONAL",
  "gstin": "27AAPFU0939F1ZV"
}
```

**Response (200 OK):**
```json
{
  "subscription_id": "sub_rzp_123456",
  "base_subtotal_inr": 49999.0,
  "gst_amount_inr": 8999.82,
  "total_amount_inr": 58998.82,
  "currency": "INR",
  "sac_code": "998314"
}
```

### `POST /api-keys`
Generates a new scoped REST API key for ERP/PLM integrations.

### `POST /webhooks`
Registers an outbound webhook destination for pipeline events (`job.validated`, `job.signed_off`).
