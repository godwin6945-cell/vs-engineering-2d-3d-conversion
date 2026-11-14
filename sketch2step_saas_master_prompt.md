# MASTER PROMPT: Sketch2STEP Enterprise (paste into Claude Code)

You are a principal engineer, CAD/CAM domain expert and product designer. Build **Sketch2STEP Enterprise**, a multi-tenant B2B SaaS that will be sold to machining and manufacturing companies at roughly ₹3–6 lakh per company. Work in the phases listed at the end. After each phase, run the tests, summarise what you built, and wait for my "continue" before starting the next one. Do not generate everything in one shot.

---

## 1. Product

Engineers upload a 2D drawing (PNG, JPG, PDF, DXF). Claude reads it and extracts every dimension, tolerance, hole, thread and feature. **Any value that is missing, unclear or unverified must be entered or confirmed by a human.** The system then builds a parametric 3D model with CadQuery, validates the geometry against the confirmed spec, and exports a STEP file plus an inspection report.

### The accuracy rule (most important)
100% accuracy cannot be guaranteed by any AI. So the product guarantees this instead: **no dimension reaches the STEP file unless it was read and cross-checked, or confirmed by a human; and the final model is measured and compared back against the confirmed spec.** Never silently guess a value. Never use marketing copy that claims "100% accurate"; use "every dimension verified before export".

---

## 2. Stack (use exactly this unless you find a strong reason, and tell me why)

**Frontend**
- Next.js 15 (App Router), TypeScript strict, React 19
- Tailwind CSS v4 + shadcn/ui + Radix primitives, Lucide icons
- TanStack Query (server state), Zustand (UI state), React Hook Form + Zod
- three.js + `occt-import-js` for in-browser STEP preview; `react-zoom-pan-pinch` for drawing viewer
- Playwright for E2E tests, Vitest for unit tests

**Backend (Python, because CadQuery is Python)**
- Python 3.11, FastAPI, Pydantic v2, SQLAlchemy 2 + Alembic, `uv` for dependency management
- PostgreSQL 16 (row-level tenant isolation), Redis 7, ARQ (or Celery) for background jobs
- S3-compatible object storage (MinIO in dev, AWS S3 / Cloudflare R2 in prod); signed URLs only
- Auth: Clerk or Keycloak (email, Google, and **SAML/OIDC SSO for enterprise**), RBAC
- Billing: **Razorpay** (India, INR, GST invoices) with Stripe as optional second provider
- Observability: structured logging, OpenTelemetry, Sentry, Prometheus metrics

**CAD / geometry**
- `cadquery` (primary), `build123d` (secondary), `cadquery-ocp` (OpenCascade bindings for validation)
- `trimesh` + `pyrender` or `vtk` for headless orthographic renders of the STEP (used for visual comparison)
- `ezdxf` (read DXF drawings directly; DXF input is exact and bypasses vision errors)
- `PyMuPDF` (PDF drawings, vector text extraction), `opencv-python-headless`, `Pillow`

**AI**
- `anthropic` Python SDK (latest). Models set by env: `EXTRACT_MODEL` default `claude-opus-5-5`, `CODEGEN_MODEL` default `claude-sonnet-5-5`. Check https://docs.claude.com for current model names and features before coding.
- Use **tool use / structured outputs** with Pydantic schemas, never free-text JSON parsing
- Use prompt caching for system prompts and the drawing image
- `PaddleOCR` (or `rapidocr-onnxruntime`) as an **independent second reader** of dimension text, to cross-check Claude
- Optional: `instructor` for schema-validated LLM output with auto-retry

**Infra**
- Docker + docker-compose for dev and single-server deployment; Helm chart or Terraform optional
- CAD code execution workers run in **isolated sandboxes** (see section 6)
- GitHub Actions CI: lint (ruff, mypy, eslint), tests, container build

---

## 3. Core pipeline (build this as an explicit state machine)

States: `UPLOADED → PREPROCESSED → EXTRACTED → NEEDS_REVIEW → CONFIRMED → MODELLED → VALIDATED → SIGNED_OFF → EXPORTED` (plus `FAILED` with reason).

1. **Preprocess.** DXF: parse entities directly with ezdxf. PDF: extract vector text and render pages at 300 DPI. Images: deskew, denoise, upscale small text. Detect multiple views (front/top/side) and crop them.
2. **Extract (two independent passes).** Run Claude twice with different prompts (and optionally different models). Each pass returns a `DrawingSpec` schema (below). Run OCR separately on the same image.
3. **Reconcile.** Compare pass A, pass B and OCR per dimension. Agree on all three and the value is printed in the drawing → `verified_auto`. Any disagreement, inferred value, or missing value → `needs_human`. Also run engineering sanity checks (below).
4. **Human review.** UI blocks the "Generate" button until every `needs_human` item is resolved.
5. **Model.** Convert the confirmed spec into geometry using the **deterministic feature compiler** first (section 4). Use Claude-written CadQuery code only as a fallback, and mark those jobs "AI-generated geometry, extra review required".
6. **Validate geometry.** Measure the actual solid with OpenCascade and compare to spec (section 5).
7. **Visual comparison.** Render orthographic views of the STEP, show side-by-side with the original drawing, and let Claude produce a "differences found" list. Show it to the human.
8. **Sign-off.** A named user approves. Store who, when, and what changed.
9. **Export.** STEP (AP214), the CadQuery script, and a PDF **inspection report**.

### DrawingSpec schema (Pydantic)
Each dimension: `id`, `name`, `value`, `unit`, `tol_plus`, `tol_minus`, `type` (linear, diameter, radius, angle, depth, thread), `source` (`printed` | `inferred` | `missing`), `confidence` (0–1), `bbox` (normalised coordinates on the image so the UI can highlight it), `view`, `status` (`verified_auto` | `needs_human` | `human_confirmed` | `human_entered`).
Also: `features[]` (hole, slot, pocket, boss, fillet, chamfer, thread, pattern) each referencing dimension ids, `material`, `general_tolerance`, `notes`, `ambiguities[]`.

### Sanity checks (engineering rules engine, pure Python, unit tested)
Overall length equals the sum of segment dimensions; hole edge distance greater than 0 and inside the part; fillet radius not larger than the adjacent feature; thread callouts match standard tables (ISO metric M-series tap drill sizes); units consistent; tolerance band valid; pattern counts match pitch × spacing. Failed rule → flag with an explanation.

---

## 4. Deterministic feature compiler (key to reliability)

Create a library of tested, parametric CadQuery builders: plate, block, cylinder/shaft (turned parts with steps), flange, bracket (L, U), counterbore/countersink/through/blind hole, hole patterns (linear, circular, grid), slot, pocket (rect/circle/obround), boss, fillet, chamfer, simple threads (cosmetic + modelled option), keyway. Each builder takes validated numbers, never raw strings, and has unit tests with expected volume and bounding box.
The LLM selects and parameterises features. It does not write arbitrary code, except in the fallback path (section 6 rules apply).

---

## 5. Geometry validation and inspection report

After modelling, use OCP/CadQuery to measure: bounding box, volume, face and edge counts, hole count and diameters, `isValid()`, shell closed, no self-intersection, STEP re-import round trip. Compare each against the confirmed spec with tolerances. Generate a PDF report: drawing thumbnail, dimension table (specified vs measured vs delta vs pass/fail), source of each value (printed, OCR-agreed, human-entered by whom), sign-off block, job ID, model versions, timestamp. This report is a major selling point for QA-conscious buyers.

---

## 6. Security (non-negotiable, because customers upload proprietary drawings)

- Multi-tenancy: every table has `org_id`; enforce with Postgres row-level security and tests that prove cross-tenant access fails.
- CAD/code execution only inside a sandbox: one-shot container per job, no network, read-only filesystem except a tmp dir, CPU/memory/time limits, non-root user, seccomp profile (gVisor or Firecracker if available). Static AST allow-list before running (only `cadquery`, `math`). Never `exec` in the API process.
- Encrypt at rest (S3 SSE, Postgres encryption), TLS everywhere, signed URLs that expire, virus scan on upload (ClamAV), file type/size validation.
- Secrets in env/secret manager only. Support **BYOK**: the company can store its own Anthropic API key (encrypted with envelope encryption), or use the platform key with usage metering.
- Audit log (append-only) for upload, view, edit, approve, export, download, login, role change.
- Data retention settings per org, hard-delete on request, no training on customer data (state this in docs).
- Rate limiting, CSRF/CORS correct, dependency scanning, SBOM.
- Provide an **on-premise / private-cloud deployment mode** (docker-compose + Helm) since many Indian manufacturers will ask for it.

---

## 7. SaaS features

- Organisations, teams, roles: Owner, Admin, Engineer, Reviewer (approve only), Viewer
- Projects and folders, versioning of every job (re-run with changed dimensions creates v2, with diff)
- Usage metering and plans (e.g. Starter, Business, Enterprise), seat and job limits, Razorpay subscriptions, GST-compliant invoices, trial mode
- Admin console: usage, cost per job (Claude tokens), failed jobs, audit log export (CSV)
- Webhooks and REST API with API keys (so customers integrate with their ERP/PLM)
- Email notifications (job done, review needed, approval requested)
- Dimension library: companies save their standard parts and recurring tolerances; reuse for faster, more accurate runs
- i18n-ready (English first, Tamil and Hindi later), INR as default currency

---

## 8. UI/UX direction

Audience: manufacturing engineers and QA leads on desktop monitors, often wearing a shop-floor mindset: they want clarity, speed, and proof. The interface should feel like precision engineering software, calm and exact, not a generic AI chat tool.

Design rules:
- Avoid cliché AI-product looks (purple gradients, glassmorphism, chat bubbles, sparkle icons). Use a restrained, confident palette: cool neutrals, one coolant-teal accent, amber reserved strictly for "needs human attention", red only for failures, green for verified.
- Typography: IBM Plex Sans for UI, IBM Plex Mono for all numeric values (tabular figures, right aligned).
- Light and dark theme, WCAG AA contrast, visible keyboard focus, reduced-motion support, full keyboard operation.
- Motion only to explain state changes. No decorative animation.

Key screens:
1. **Dashboard:** jobs by state, "Needs your review" queue first, usage meter.
2. **Review workspace (the hero screen):** split layout. Left: drawing viewer with zoom/pan; every extracted dimension is drawn as an overlay box. Right: dimension table grouped by status (Needs input, Estimated, Verified). **Clicking a row highlights its location on the drawing, and clicking a box on the drawing jumps to its row.** Missing values show an empty, required input with a clear label such as "Not found on drawing. Enter value (mm)". Show each value's evidence: "Claude A: 24.0 · Claude B: 24.0 · OCR: 24.0". Keyboard: Enter to confirm and move to next, J/K to move, E to edit. A progress bar "18 of 24 verified" and a disabled primary button "Generate model" until zero items need input.
3. **Model review:** 3D viewer (orbit, section view, measure tool, toggle wireframe) beside the original drawing with overlay/slider comparison; validation table with pass/fail; the AI "differences found" list.
4. **Sign-off and export:** summary, approve button (role-gated), downloads (STEP, script, PDF report).
5. **Settings:** team, API keys (BYOK), billing, security (SSO), retention, audit log.
6. Empty states that teach, error messages that say what failed and what to do next.

Build a small design-token file and reusable components (DimensionRow, EvidenceChips, StatusBadge, DrawingViewer, ModelViewer, ReviewProgress). Provide Storybook or an equivalent component gallery.

---

## 9. Accuracy evaluation harness (build this early)

- Create `eval/` with a dataset format: drawing file + ground-truth spec + ground-truth STEP. I will supply real drawings; generate 30 synthetic ones with CadQuery and ezdxf for now.
- Metrics: dimension extraction precision/recall, exact-match rate, false "verified" rate (the most dangerous error; target near zero), % jobs needing human input, geometry deviation vs ground truth, cost and latency per job.
- A CI job runs the eval on every prompt or model change and blocks regressions. Log model, prompt version and results for every job.

---

## 10. Repository layout

```
/apps/web            Next.js frontend
/apps/api            FastAPI service
/apps/worker         ARQ workers (preprocess, extract, model, validate, report)
/packages/cad        feature compiler, validators (pure Python, heavily tested)
/packages/spec       shared schemas (Pydantic → generated TypeScript types)
/eval                datasets and evaluation runner
/infra               docker, compose, helm, terraform
/docs                architecture, security, API reference, runbooks
```
Provide `.env.example` with a placeholder `ANTHROPIC_API_KEY=your-api-key-here` and all other variables, plus a one-command `make dev` and `make test`.

---

## 11. Build phases (stop after each and wait for "continue")

1. **Foundations:** repo, docker-compose (Postgres, Redis, MinIO), FastAPI + Next.js skeleton, auth, orgs, RBAC, RLS tests, CI.
2. **CAD core:** feature compiler, validators, STEP export, 40+ unit tests. No AI yet.
3. **AI extraction:** preprocessing, two-pass extraction with structured outputs, OCR cross-check, reconciliation, rules engine.
4. **Review workspace UI:** the hero screen with overlays, evidence, required inputs, keyboard flow.
5. **Modelling and validation:** compiler integration, fallback codegen in sandbox, geometry validation, visual comparison, 3D viewer.
6. **Sign-off, versioning, PDF inspection report, audit log.**
7. **SaaS layer:** Razorpay billing, plans, usage metering, admin console, webhooks, API keys, email.
8. **Hardening:** security review, load test, eval harness gating, backups, on-prem package, documentation, demo dataset and demo mode.

At the start, ask me up to five clarifying questions (target part types, drawing standards such as ISO/ASME, expected volume per month, deployment preference, languages). Then begin Phase 1.
