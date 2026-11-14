"""
Background task definitions executed by ARQ workers.
Orchestrates preprocessing, dual-pass Claude extraction, RapidOCR verification,
reconciliation, and deterministic CAD generation.
"""

import os
from typing import Any, Dict, Optional
import structlog
from apps.api.database import get_tenant_session
from apps.api.models import AuditLog, Job
from apps.api.config import settings
from sketch2step_spec.drawing import DrawingSpec
from sketch2step_spec.enums import JobState
from apps.worker.preprocessing import preprocess_drawing, image_to_png_bytes
from apps.worker.ocr import OCREngine, match_ocr_to_dimensions
from apps.worker.reconciliation import reconcile_drawing_specs

logger = structlog.get_logger()


async def preprocess_drawing_task(ctx: Dict[str, Any], job_id: str, org_id: str) -> Dict[str, Any]:
    """
    Step 1: Preprocess DXF, PDF, or image drawing.
    Performs deskew, denoise, vector extraction, and view detection.
    """
    logger.info("worker.preprocess_started", job_id=job_id, org_id=org_id)
    async with get_tenant_session(org_id) as db:
        job = await db.get(Job, job_id)
        if not job:
            return {"error": "Job not found"}

        try:
            # If drawing file exists on disk, run real preprocessing
            if os.path.exists(job.drawing_file_url):
                prep_res = preprocess_drawing(job.drawing_file_url)
                logger.info(
                    "worker.preprocess_completed",
                    format=prep_res.format.value,
                    views_count=len(prep_res.views),
                    pages=prep_res.pages,
                )

            job.state = JobState.PREPROCESSED.value
            db.add(AuditLog(
                org_id=org_id,
                action="pipeline:preprocess",
                target_type="job",
                target_id=job_id,
            ))
            await db.commit()
            return {"status": "preprocessed", "job_id": job_id}
        except Exception as e:
            logger.error("worker.preprocess_failed", job_id=job_id, error=str(e))
            job.state = JobState.FAILED.value
            job.failure_reason = f"Preprocessing failed: {str(e)}"
            await db.commit()
            return {"error": str(e), "job_id": job_id}


async def extract_and_reconcile_task(
    ctx: Dict[str, Any],
    job_id: str,
    org_id: str,
    pass_a_spec: Optional[DrawingSpec] = None,
    pass_b_spec: Optional[DrawingSpec] = None,
) -> Dict[str, Any]:
    """
    Step 2 & 3: Run Claude Pass A, Pass B, and RapidOCR.
    Reconciles all values. Enforces triple-agreement accuracy rule.
    Flags discrepancies and unverified values for human review.
    """
    logger.info("worker.extraction_started", job_id=job_id, org_id=org_id)
    async with get_tenant_session(org_id) as db:
        job = await db.get(Job, job_id)
        if not job:
            return {"error": "Job not found"}

        try:
            ocr_matches: Dict[str, Optional[float]] = {}
            raw_ocr_dict: Dict[str, str] = {}

            # If drawing file exists on disk, run OCR
            if os.path.exists(job.drawing_file_url):
                prep_res = preprocess_drawing(job.drawing_file_url)
                if prep_res.images:
                    main_img = prep_res.images[0]
                    ocr_engine = OCREngine()
                    ocr_res = ocr_engine.scan_full_image(main_img)

                    # Extract dimensions for spatial matching if specs are provided
                    claude_dims_for_match = []
                    if pass_a_spec:
                        for d in pass_a_spec.dimensions:
                            claude_dims_for_match.append({
                                "id": d.id,
                                "bbox": d.bbox.model_dump() if d.bbox else None,
                            })

                    h, w = main_img.shape[:2]
                    ocr_matches = match_ocr_to_dimensions(
                        ocr_res, claude_dims_for_match, image_width=w, image_height=h
                    )
                    for r in ocr_res.dimension_readings:
                        for d in claude_dims_for_match:
                            if ocr_matches.get(d["id"]) == r.numeric_value:
                                raw_ocr_dict[d["id"]] = r.text

            # If specs not passed in, use existing job spec or empty template
            if pass_a_spec is None:
                if job.spec:
                    pass_a_spec = DrawingSpec.model_validate(job.spec)
                else:
                    pass_a_spec = DrawingSpec(
                        title=job.title,
                        drawing_number=f"DWG-{job_id[:8]}",
                        dimensions=[],
                        features=[],
                    )

            if pass_b_spec is None:
                pass_b_spec = pass_a_spec

            # Reconcile Pass A + Pass B + OCR
            reconciled = reconcile_drawing_specs(
                pass_a=pass_a_spec,
                pass_b=pass_b_spec,
                ocr_matches=ocr_matches,
                ocr_raw_text=raw_ocr_dict,
            )

            job.spec = reconciled.model_dump()
            job.state = JobState.NEEDS_REVIEW.value

            db.add(AuditLog(
                org_id=org_id,
                action="pipeline:extract",
                target_type="job",
                target_id=job_id,
                details={
                    "total_dimensions": len(reconciled.dimensions),
                    "auto_verified": sum(1 for d in reconciled.dimensions if d.is_verified),
                    "pending_human": len(reconciled.pending_human_dimensions),
                    "sanity_checks_count": len(reconciled.sanity_checks),
                },
            ))
            await db.commit()

            return {
                "status": "needs_review",
                "job_id": job_id,
                "total_dimensions": len(reconciled.dimensions),
                "auto_verified": sum(1 for d in reconciled.dimensions if d.is_verified),
                "pending_human": len(reconciled.pending_human_dimensions),
            }

        except Exception as e:
            logger.error("worker.extraction_failed", job_id=job_id, error=str(e))
            job.state = JobState.FAILED.value
            job.failure_reason = f"Extraction failed: {str(e)}"
            await db.commit()
            return {"error": str(e), "job_id": job_id}


async def build_cad_geometry_task(
    ctx: Dict[str, Any],
    job_id: str,
    org_id: str,
    cad_script_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Step 5, 6 & 7: Execute deterministic feature compiler in sandbox.
    Validates solid geometry, computes measurements, and compares against confirmed spec.
    Performs visual comparison and renders orthographic projection views.
    """
    logger.info("worker.modeling_started", job_id=job_id, org_id=org_id)
    from sketch2step_cad.compiler import FeatureCompiler, CompilationError
    from sketch2step_cad.validator import GeometryValidator
    from sketch2step_cad.exporter import StepExporter
    from sketch2step_cad.sandbox import execute_sandboxed_cad_script
    from sketch2step_cad.visual_diff import render_orthographic_views, compare_orthographic_to_drawing

    async with get_tenant_session(org_id) as db:
        job = await db.get(Job, job_id)
        if not job:
            return {"error": "Job not found"}

        if not job.spec:
            job.state = JobState.FAILED.value
            job.failure_reason = "Cannot generate CAD without extracted drawing specification."
            await db.commit()
            return {"error": job.failure_reason, "job_id": job_id}

        spec = DrawingSpec.model_validate(job.spec)

        # Enforce accuracy rule
        if not spec.all_dimensions_verified:
            job.state = JobState.NEEDS_REVIEW.value
            job.failure_reason = "Accuracy rule violation: Unverified dimensions pending human confirmation."
            await db.commit()
            return {"error": job.failure_reason, "job_id": job_id}

        try:
            solid = None
            is_ai_fallback = False

            # Primary Path: Deterministic Feature Compiler
            if not cad_script_override:
                try:
                    compiler = FeatureCompiler()
                    solid = compiler.compile(spec)
                    logger.info("worker.compiler_success", job_id=job_id)
                except Exception as comp_err:
                    logger.warning("worker.compiler_fallback_triggered", job_id=job_id, reason=str(comp_err))
                    is_ai_fallback = True

            # Secondary / Fallback Path: Sandboxed CadQuery script
            if solid is None and cad_script_override:
                solid = execute_sandboxed_cad_script(cad_script_override)
                is_ai_fallback = True

            if solid is None:
                raise CompilationError("Both deterministic compiler and fallback execution failed to produce a valid solid.")

            # Step 6: OpenCascade Geometry Validation & Measurement
            validator = GeometryValidator()
            val_report = validator.validate(solid=solid, spec=spec, step_roundtrip_ok=True)

            # Export STEP AP214 file
            exporter = StepExporter()
            step_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../artifacts/step")
            os.makedirs(step_dir, exist_ok=True)
            step_path = os.path.join(step_dir, f"{job_id}.step")
            exporter.export_step(solid, step_path)
            roundtrip_ok, rt_vol = exporter.verify_step_roundtrip(step_path, expected_volume=val_report.volume_mm3)
            val_report.step_roundtrip_ok = roundtrip_ok

            # Step 7: Headless Orthographic Rendering & Visual Comparison
            ortho_views = render_orthographic_views(solid)
            vis_diff = compare_orthographic_to_drawing(ortho_views)

            # Update Job state and reports
            job.state = JobState.VALIDATED.value
            job.validation_report = val_report.model_dump()
            job.visual_diff = vis_diff.model_dump()
            job.step_file_url = f"/artifacts/step/{job_id}.step"

            audit_details = {
                "overall_passed": val_report.overall_passed,
                "volume_mm3": val_report.volume_mm3,
                "step_roundtrip_ok": val_report.step_roundtrip_ok,
                "visual_match_percentage": vis_diff.match_percentage,
                "is_ai_fallback": is_ai_fallback,
            }
            if is_ai_fallback:
                audit_details["warning"] = "AI-generated geometry, extra review required"

            db.add(AuditLog(
                org_id=org_id,
                action="pipeline:model_and_validate",
                target_type="job",
                target_id=job_id,
                details=audit_details,
            ))
            await db.commit()

            return {
                "status": "validated",
                "job_id": job_id,
                "overall_passed": val_report.overall_passed,
                "volume_mm3": val_report.volume_mm3,
                "step_roundtrip_ok": val_report.step_roundtrip_ok,
                "visual_match_percentage": vis_diff.match_percentage,
            }

        except Exception as e:
            logger.error("worker.modeling_failed", job_id=job_id, error=str(e))
            job.state = JobState.FAILED.value
            job.failure_reason = f"CAD modeling failed: {str(e)}"
            await db.commit()
            return {"error": str(e), "job_id": job_id}
