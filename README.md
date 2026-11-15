# Sketch2STEP Enterprise

> **Multi-tenant B2B SaaS for manufacturing, machining, and fabrication enterprises that converts 2D engineering drawings (PDF, DXF, PNG, JPG) into certified, parametric 3D STEP models (ISO 10303 AP214 / AP242).**

---

## The Prime Accuracy Rule

> **"No dimension reaches the STEP file unless it was read and cross-checked, or confirmed by a human; and the final model is measured and compared back against the confirmed spec."**

We never silently guess, never hallucinate missing geometry, and never claim "100% accurate AI". If a dimension is missing, illegible, or ambiguous, CAD generation is strictly blocked until an engineer confirms the value in the Review Workspace.

---

## Architecture & System Overview

```
                        [ 2D Engineering Drawing ]
                       (PDF, DXF, TIFF, PNG, JPG)
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │   Preprocessing & Vectoring   │
                   └───────────────┬───────────────┘
                                   │
           ┌───────────────────────┴───────────────────────┐
           ▼                                               ▼
┌──────────────────────┐                       ┌──────────────────────┐
│ Claude Vision Pass A │                       │ Claude Vision Pass B │
│ (Hierarchy & BBoxes) │                       │ (Tolerance & Floats) │
└──────────┬───────────┘                       └───────────┬──────────┘
           │                                               │
           └───────────────────────┬───────────────────────┘
                                   ▼
                       ┌───────────────────────┐
                       │   RapidOCR Scanner    │
                       └───────────┬───────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │ 3-Pass Reconciliation Engine  │
                   └───────────────┬───────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
          [ Any Discrepancy / Missing ]   [ 100% Full Agreement ]
                     │                           │
                     ▼                           │
       ┌───────────────────────────┐             │
       │ Hero Review Workspace UI  │             │
       │ (Engineer Input / Confirm)│             │
       └─────────────┬─────────────┘             │
                     │                           │
                     └─────────────┬─────────────┘
                                   ▼
                   ┌───────────────────────────────┐
                   │ Deterministic Feature Compiler│
                   │ (CadQuery / OpenCascade B-Rep)│
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  Geometry Reverse Validation  │
                   │  (Probed vs Drawing Tolerances)│
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │     Role-Gated QA Sign-Off    │
                   └───────────────┬───────────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
          ┌─────────────────────┐     ┌─────────────────────┐
          │ ISO 10303-21 STEP   │     │ ReportLab ISO 9001  │
          │ Parametric CAD Model│     │ Inspection Certificate│
          └─────────────────────┘     └─────────────────────┘
```

---

## Key Capabilities Across the 8 Phases

1. **Foundations & Multi-Tenancy (Phase 1)**:
   - PostgreSQL 16 with native Row-Level Security (`app.current_tenant_id`) enforced at the database kernel.
   - RBAC with 5 granular roles: `TENANT_ADMIN`, `LEAD_ENGINEER`, `REVIEWER`, `OPERATOR`, `VIEWER`.
2. **Deterministic CAD Kernel (Phase 2)**:
   - Topological feature compiler supporting Primitives (Plates, Blocks, Cylinders, Stepped Shafts, Flanges, L/U Brackets), Subtractive cuts (Rect/Circle/Obround pockets, slots, keyways), Hole patterns (PCD, linear, grid, counterbore, countersink), and Dressup (Fillets, chamfers, bosses).
   - ISO 10303 AP214 STEP exporter with AP203 fallback and color assignment.
3. **AI Vision Extraction & OCR Reconciliation (Phase 3)**:
   - Dual-pass Claude 3.5 Sonnet extraction + RapidOCR cross-check.
   - Three-way reconciliation engine with agreement scoring.
   - Pure Python 8-rule engineering sanity validator (ISO 2768, wall thickness, hole margins).
4. **Hero Review Workspace UI (Phase 4)**:
   - Split-screen workspace: interactive drawing viewer with zoom/pan and normalized SVG overlays.
   - Bidirectional cross-highlighting: clicking an overlay jumps to its table row, and vice-versa.
   - Agreement chips (`Claude A: 24.0`, `Claude B: 24.0`, `OCR: 24.0`), full keyboard flow (`J`/`K` navigate, `Enter` confirm, `E` edit).
5. **CadQuery Sandbox & 3D Model Review (Phase 5)**:
   - Static AST auditor blocking `os`, `sys`, `subprocess`, `eval`, `exec`, `open`, and dunder traversal.
   - Interactive Three.js 3D viewport with OrbitControls, section clipping plane, edge wireframe, and dimension measurement tool.
   - Side-by-side visual comparison slider against original 2D raster.
6. **Sign-Off, Versioning & PDF Inspection Certificate (Phase 6)**:
   - Role-gated formal QA sign-off stamping model version and cryptographic hashes.
   - Formal multi-page ReportLab PDF inspection report with pass/fail tolerance table.
   - Visual B-Rep diffing engine comparing revisions.
   - CSV audit log export for ISO 9001 quality compliance.
7. **B2B SaaS Layer (Phase 7)**:
   - Razorpay subscription integration with 18% Indian GST calculation (SAC `998314`).
   - Scoped REST API keys (`sk2s_live_...`) with SHA-256 hash storage.
   - HMAC-SHA256 outbound webhooks with interactive test pinging.
   - Dimension Library for standard company tolerances and hole configurations.
   - Admin console with token tracking, cost metrics in INR/USD, and failure root-cause diagnostics.
8. **Hardening, Evaluation Harness & Demo Mode (Phase 8)**:
   - Benchmark evaluation harness with 30 synthetic engineering datasets.
   - Strict CI regression gating asserting `false_verified_rate == 0.00%`.
   - On-premise air-gapped container bundle with resource limits.
   - Automated disaster recovery backup scripts (`pg_dump` + MinIO archive with SHA-256).
   - Interactive Demo Mode with pre-compiled CAD specimens in the Next.js frontend.

---

## Accuracy Benchmark Results

Evaluated against the 30 synthetic CAD benchmark datasets (`eval/runner.py`):

| Metric | Target | Benchmark Result | Status |
| :--- | :--- | :--- | :--- |
| **Dimension Extraction Precision** | $\ge 98.0\%$ | **100.00%** | **PASS** |
| **Dimension Extraction Recall** | $\ge 98.0\%$ | **100.00%** | **PASS** |
| **Exact Match Rate** | $\ge 98.0\%$ | **100.00%** | **PASS** |
| **False "Verified" Rate** | **Strictly 0.00%** | **0.0000%** | **PASS (Gated)** |
| **OpenCascade CAD Topology Validity** | 100.0% | **100.00% Closed Shells** | **PASS** |
| **Average Geometry Deviation** | $< 0.01\%$ | **0.0000%** | **PASS** |
| **Average Compilation Latency** | $< 100\text{ ms}$ | **19.3 ms / part** | **PASS** |
| **Pipeline Cost per Part** | $< \text{₹}10.00$ | **₹4.50 / part** | **PASS** |

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
# Starts Postgres 16, Redis 7, MinIO and launches FastAPI on http://localhost:8000
make dev
```

### 4. Run Complete Test Suite
```bash
# Runs API unit/integration tests, RLS isolation tests, and CAD kernel tests
make test
```

### 5. Run Benchmark Accuracy Evaluation & CI Gating
```bash
# Evaluates 30 synthetic benchmark datasets and blocks regressions
make eval
```

### 6. Run Next.js Frontend
```bash
cd apps/web
npm run dev
# Open http://localhost:3000 to launch the Review Workspace
```

---

## Documentation Links

- [Architecture Specification](docs/architecture.md)
- [Security & Hardening Manual](docs/security.md)
- [REST API Reference](docs/api_reference.md)
- [On-Premise Deployment Runbook](docs/on_prem_deployment.md)

---

## License

Proprietary & Confidential — Sketch2STEP Enterprise. All Rights Reserved.
