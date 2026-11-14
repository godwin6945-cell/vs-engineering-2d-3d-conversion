"""
Unit tests for the PDF Inspection Report Generator.
"""

from datetime import datetime, timezone
import pytest
from sketch2step_cad.report_pdf import PDFReportGenerator
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec
from sketch2step_spec.job import GeometryMeasurement, ValidationReport


@pytest.fixture
def sample_spec_and_validation():
    spec = DrawingSpec(
        drawing_number="DWG-2026-FLG-04",
        title="Precision Flange Adapter",
        revision="B",
        material="Aluminum 6061-T6",
        general_tolerance="ISO 2768-m",
        dimensions=[
            DimensionSpec(id="d1", name="Overall Length", value=120.0),
            DimensionSpec(id="d2", name="Overall Width", value=80.0),
        ],
    )

    validation = ValidationReport(
        is_valid_solid=True,
        is_shell_closed=True,
        has_self_intersections=False,
        bounding_box_x=120.0,
        bounding_box_y=80.0,
        bounding_box_z=35.0,
        volume_mm3=245800.0,
        surface_area_mm2=48900.0,
        face_count=18,
        edge_count=42,
        hole_count=5,
        step_roundtrip_ok=True,
        overall_passed=True,
        measurements=[
            GeometryMeasurement(
                name="Overall Length",
                dimension_id="d1",
                specified_value=120.0,
                measured_value=120.0,
                tolerance_plus=0.1,
                tolerance_minus=0.1,
                deviation=0.0,
                passed=True,
                source_attribution="verified_auto (Claude A + B + OCR)",
            ),
            GeometryMeasurement(
                name="Overall Width",
                dimension_id="d2",
                specified_value=80.0,
                measured_value=80.0,
                tolerance_plus=0.1,
                tolerance_minus=0.1,
                deviation=0.0,
                passed=True,
                source_attribution="verified_auto (Claude A + B + OCR)",
            ),
        ],
    )

    return spec, validation


def test_generate_inspection_pdf_valid(sample_spec_and_validation):
    spec, validation = sample_spec_and_validation

    pdf_bytes = PDFReportGenerator.generate_inspection_pdf(
        job_id="test_job_12345678",
        spec=spec,
        validation=validation,
        signed_off_by="Jane Doe, QA Principal",
        signed_off_at=datetime.now(timezone.utc),
        model_version=1,
        tenant_name="Alpha Precision Works",
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000  # Non-empty PDF
    assert pdf_bytes.startswith(b"%PDF-")  # Valid PDF signature
    assert b"%%EOF" in pdf_bytes[-1024:]  # Valid PDF footer
