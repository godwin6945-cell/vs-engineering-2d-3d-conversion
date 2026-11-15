# Sketch2STEP Enterprise — Security & Hardening Manual

## 1. Threat Model & Security Posture

Sketch2STEP Enterprise is architected under the assumption that 2D engineering drawings represent high-value proprietary intellectual property (IP), and that automated CAD generation poses potential physical machining risks if models deviate from tolerance.

### Threat Vectors Addressed:
1. **Multi-Tenant Cross-Contamination**: Prevent Tenant A from accessing Tenant B's drawings, specs, or models.
2. **Arbitrary Code Execution via Fallback CadQuery Scripts**: Prevent untrusted AI or user-crafted Python scripts from compromising the host server or network.
3. **API Key & Webhook Tampering**: Ensure external ERP/PLM integrations are cryptographically signed and scoped.
4. **Credential Exposure at Rest**: Encrypt BYOK Claude API keys using defense-in-depth envelope encryption.

---

## 2. PostgreSQL Row-Level Security (RLS)

Every database table holding customer data has PostgreSQL Row-Level Security enabled:
```sql
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON jobs
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid);
```

### Connection Session Setting:
Whenever an API request authenticates a tenant via JWT or REST API key, the database session acquires a connection and sets the tenant context:
```python
await session.execute(text(f"SET LOCAL app.current_tenant_id = '{tenant_id}';"))
```
Even if an application-level SQL query forgets a `WHERE tenant_id = ...` clause, the database kernel strictly filters out rows belonging to other tenants.

---

## 3. Sandboxed Execution & Static AST Auditor

When parametric feature compilation requires fallback code synthesis, the code is audited **before** execution using `CADSecurityAuditor`:

### 3.1. Forbidden Nodes & Constructs
- **Imports**: ONLY `cadquery`, `cq`, and `math` are permitted. All other module imports (`os`, `sys`, `subprocess`, `socket`, `shutil`, `urllib`, `requests`) are blocked and raise `SecurityViolation`.
- **Builtins**: Dangerous functions (`eval`, `exec`, `compile`, `open`, `breakpoint`, `globals`, `locals`, `vars`, `getattr`, `setattr`, `hasattr`, `delattr`) are stripped from `__builtins__`.
- **Dunder Reflection**: Attribute lookups targeting `__class__`, `__bases__`, `__subclasses__`, `__globals__`, `__code__`, `__mro__` are intercepted at parse time.
- **Execution Limits**: Runs inside a sub-thread with strict execution timeouts (default 15s) and memory caps.

---

## 4. BYOK Envelope Encryption (AES-256-GCM)

Enterprises that provide their own Anthropic API key benefit from envelope encryption:
1. **Master Key**: Stored securely in an external KMS/vault (`ENCRYPTION_MASTER_KEY`).
2. **Tenant Key Derivation**: HKDF-SHA256 derives a unique encryption key per tenant using the `tenant_id` as the salt context.
3. **Cipher**: AES-256 in Galois/Counter Mode (GCM), providing authenticated encryption with an initialization vector (IV) and authentication tag.
4. **Decryption on Demand**: Decrypted only in memory inside the worker job during the inference pass and never persisted in logs or audit trails.

---

## 5. API Key & Webhook Security

### API Keys
- Generated with `sk2s_live_` prefix and 32 bytes of cryptographically secure random entropy (`secrets.token_urlsafe(32)`).
- Raw token is presented to the user **once** upon creation.
- Only the SHA-256 hash is persisted in the database.
- Permission scopes:
  - `job:create`: Upload drawings and trigger pipelines.
  - `job:read`: Query job status, review spec, and fetch metadata.
  - `export:download`: Download STEP models and ISO QA certificates.

### Webhook Signatures
Every outbound event payload sent to external webhooks includes an HMAC-SHA256 signature in the `X-Sketch2Step-Signature` header:
$$\text{Signature} = \text{HMAC-SHA256}(\text{Secret}, \text{Payload JSON})$$
Consumers verify authenticity by comparing the header with their pre-shared webhook secret using constant-time comparison (`hmac.compare_digest`).

---

## 6. Immutable Audit Trail

Every state change, dimension edit, manual confirmation, and QA sign-off writes an append-only row to the `audit_logs` table:
- `actor_id` & `actor_email`
- `action` (e.g., `DIMENSION_CONFIRMED`, `CAD_COMPILED`, `QA_SIGNED_OFF`)
- `ip_address`
- `details` (exact old value, new value, tolerance, and timestamp)
- Exportable to CSV for ISO 9001 quality audits.
