# Sketch2STEP Enterprise API Reference

All requests must supply `Authorization: Bearer <token>` header (except `/health` and auth endpoints).

## Endpoints Summary

### Authentication
- `POST /api/v1/auth/register` - Create new tenant organization and initial Owner account.
- `POST /api/v1/auth/login` - Authenticate user, returns tenant-scoped JWT token.
- `GET /api/v1/auth/me` - Get current user profile and role.

### Organizations & Teams
- `GET /api/v1/orgs/current` - Get tenant organization details.
- `PATCH /api/v1/orgs/current` - Update settings, retention period, and BYOK Anthropic key (Admin/Owner).
- `GET /api/v1/orgs/members` - List organization members.
- `POST /api/v1/orgs/members` - Invite/create member with role (Admin/Owner).
- `PATCH /api/v1/orgs/members/{id}/role` - Update member's RBAC role.

### Jobs & 2D-to-3D Pipelines
- `GET /api/v1/jobs` - List tenant jobs (with optional `state` filter).
- `POST /api/v1/jobs` - Upload 2D drawing and initialize pipeline.
- `GET /api/v1/jobs/{id}` - Retrieve job details, drawing URL, extracted spec, and reports.
- `PATCH /api/v1/jobs/{id}/dimensions/{dim_id}` - Human-in-the-loop confirm or enter dimension value.
- `POST /api/v1/jobs/{id}/sign-off` - QA sign-off of verified model (Reviewer/Admin/Owner).

### Compliance & Audit
- `GET /api/v1/audit-logs` - Inspect tamper-evident audit logs (Admin/Owner).
