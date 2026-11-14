"""
Inspection Report generator for QA verification.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sketch2step_spec.drawing import DrawingSpec
from sketch2step_spec.job import ValidationReport


class InspectionReportCompiler:
    """Compiles structured inspection and sign-off report for customer QA."""

    @staticmethod
    def compile_report_data(
        job_id: str,
        spec: DrawingSpec,
        validation: ValidationReport,
        signed_off_by: str,
        signed_off_at: Optional[datetime] = None,
        model_version: int = 1,
    ) -> Dict[str, Any]:
        timestamp = signed_off_at or datetime.now(timezone.utc)

        dimension_rows = []
        for m in validation.measurements:
            dimension_rows.append({
                "name": m.name,
                "dimension_id": m.dimension_id,
                "specified": m.specified_value,
                "measured": m.measured_value,
                "tolerance": f"+{m.tolerance_plus} / -{m.tolerance_minus}",
                "delta": m.deviation,
                "result": "PASS" if m.passed else "FAIL",
                "attribution": m.source_attribution,
            })

        return {
            "job_id": job_id,
            "drawing_number": spec.drawing_number or "N/A",
            "title": spec.title or "Untitled Part",
            "revision": spec.revision or "A",
            "material": spec.material or "Generic Alloy / Aluminum 6061",
            "general_tolerance": spec.general_tolerance,
            "solid_metrics": {
                "is_valid": validation.is_valid_solid,
                "is_closed": validation.is_shell_closed,
                "volume_mm3": validation.volume_mm3,
                "surface_area_mm2": validation.surface_area_mm2,
                "bounding_box": f"{validation.bounding_box_x} x {validation.bounding_box_y} x {validation.bounding_box_z} mm",
                "face_count": validation.face_count,
                "step_roundtrip_verified": validation.step_roundtrip_ok,
            },
            "overall_status": "APPROVED" if validation.overall_passed else "REJECTED",
            "dimensions_table": dimension_rows,
            "sign_off": {
                "approver": signed_off_by,
                "timestamp": timestamp.isoformat(),
                "model_version": model_version,
            },
        }
