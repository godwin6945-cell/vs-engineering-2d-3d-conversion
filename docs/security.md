# Security & Multi-Tenancy Architecture

## 1. Multi-Tenant Row-Level Security (RLS)

Every database table contains an `org_id` column. PostgreSQL Row-Level Security policies restrict rows based on `current_setting('app.current_org_id', true)`.

1. When a request authenticates via JWT, `get_current_user` extracts `org_id`.
2. The database session executes `SET LOCAL app.current_org_id = :org_id;`.
3. Any attempt by tenant B to read or modify tenant A's rows returns HTTP 404 (zero leakage).
4. Automated integration tests in `test_rls_isolation.py` run on every CI build to block regressions.

## 2. Bring Your Own Key (BYOK) Envelope Encryption

Enterprises can store their own Anthropic API keys for maximum data sovereignty:
- Keys are encrypted using AES-256-GCM with a tenant-isolated nonce.
- The master key resides exclusively in environment secrets.
- Prompts never undergo customer data model training.

## 3. Sandboxed CAD Execution

Fallback AI-generated CadQuery scripts run strictly inside isolated containers:
- Network disabled (`--network none`)
- Read-only root filesystem with ephemeral memory-backed `/tmp`
- Maximum CPU: 1.0 core, Maximum RAM: 1024 MB
- Timeout: 45 seconds
- Static AST allowlist check before execution (only `cadquery` and `math` imports allowed; `os`, `sys`, `subprocess`, `socket` strictly rejected).

## 4. Append-Only Audit Logging

All actions (`upload`, `view`, `edit`, `approve`, `export`, `download`, `login`, `role change`) are written to `audit_logs` table with user attribution, timestamp, and IP address.
