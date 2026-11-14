# Sketch2STEP Enterprise

> Multi-tenant B2B SaaS converting 2D engineering drawings (PDF, DXF, PNG, JPG) into verified parametric 3D STEP models for machining and manufacturing enterprises.

## The Accuracy Rule
**No dimension reaches the STEP file unless it was read and cross-checked, or confirmed by a human; and the final model is measured and compared back against the confirmed spec.**

---

## Repository Structure

```
├── apps/
│   ├── api/            # FastAPI backend service (Python 3.11, SQLAlchemy 2, RLS, RBAC)
│   ├── web/            # Next.js 15 frontend (TypeScript, Tailwind v4, Lucide, IBM Plex)
│   └── worker/         # ARQ Redis background workers
├── packages/
│   ├── cad/            # Deterministic CadQuery feature compiler & geometry validators
│   └── spec/           # Shared Pydantic data schemas & TypeScript type contracts
├── eval/               # Accuracy evaluation harness & synthetic benchmark runners
├── infra/              # Docker Compose (Postgres 16, Redis 7, MinIO), Dockerfiles, RLS init
└── docs/               # System architecture, security model, and API reference
```

---

## Quickstart

### 1. Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### 2. Environment Setup
```bash
cp .env.example .env
```

### 3. Run Development Stack
```bash
make dev
```

### 4. Run Tests
```bash
make test
```

All 12 foundation tests verify:
- Authentication & JWT token issuance
- RBAC permissions (Owner, Admin, Engineer, Reviewer, Viewer)
- Row-Level Security tenant isolation (cross-tenant access returns 404)
- DrawingSpec schema validation & accuracy blocking rules
