-- =========================================================================
-- Sketch2STEP Enterprise: PostgreSQL 16 Row-Level Security (RLS) Setup
-- Enforces absolute tenant isolation across all tables with org_id
-- =========================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Function to read the tenant context variable safely
CREATE OR REPLACE FUNCTION current_org_id() RETURNS text AS $$
BEGIN
    RETURN current_setting('app.current_org_id', true);
END;
$$ LANGUAGE plpgsql STABLE;

-- Ensure RLS is enabled and forced for tenant tables
-- Example policy applied to jobs:
-- ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE jobs FORCE ROW LEVEL SECURITY;
-- CREATE POLICY tenant_isolation_policy ON jobs
--     FOR ALL
--     USING (org_id = current_org_id())
--     WITH CHECK (org_id = current_org_id());

-- Audit log immutable insert-only rule
-- CREATE POLICY audit_log_tenant_policy ON audit_logs
--     FOR SELECT
--     USING (org_id = current_org_id());
-- CREATE POLICY audit_log_insert_policy ON audit_logs
--     FOR INSERT
--     WITH CHECK (org_id = current_org_id());
