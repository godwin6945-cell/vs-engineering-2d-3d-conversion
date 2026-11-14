"""
Unit tests for Geometry Validator, STEP Exporter, and Inspection Report Compiler.
"""

import os
import tempfile
import pytest
import cadquery as cq
from sketch2step_cad.exporter import StepExporter
from sketch2step_cad.report import InspectionReportCompiler
from sketch2step_cad.validator import GeometryValidator
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec
from sketch2step_spec.enums import DimensionStatus


@pytest.fixture
def sample_solid() -> cq.Workplane:
    # 100 x 50 x 20 mm plate with a central 16 mm hole
    return (
        cq.Workplane("XY")
        .box(100.0, 50.0, 20.0, centered=(True, True, False))
        .faces(">Z")
        .workplane()
        .hole(16.0)
    )


def test_geometry_validator_metrics(sample_solid: cq.Workplane):
    validator = GeometryValidator()
    report = validator.validate(sample_solid)

    assert report.is_valid_solid
    assert report.is_shell_closed
    assert not report.has_self_intersections
    assert report.bounding_box_x == 100.0
    assert report.bounding_box_y == 50.0
    assert report.bounding_box_z == 20.0
    assert report.volume_mm3 > 0.0
    assert report.face_count > 0
    assert report.edge_count > 0


def test_geometry_validator_spec_comparison(sample_solid: cq.Workplane):
    validator = GeometryValidator()

    spec = DrawingSpec(
        drawing_number="DWG-VAL-01",
        title="Inspection Plate",
        dimensions=[
            DimensionSpec(
                id="d1",
                name="Overall Length",
                value=100.0,
                tol_plus=0.1,
                tol_minus=0.1,
                status=DimensionStatus.VERIFIED_AUTO,
            ),
            DimensionSpec(
                id="d2",
                name="Overall Width",
                value=50.0,
                tol_plus=0.05,
                tol_minus=0.05,
                status=DimensionStatus.HUMAN_CONFIRMED,
                confirmed_by_user_id="lead_eng",
            ),
        ],
    )

    report = validator.validate(sample_solid, spec=spec)
    assert report.overall_passed
    assert len(report.measurements) == 2

    m_len = next(m for m in report.measurements if m.dimension_id == "d1")
    assert m_len.specified_value == 100.0
    assert m_len.measured_value == 100.0
    assert m_len.deviation == 0.0
    assert m_len.passed


def test_step_export_and_file_creation(sample_solid: cq.Workplane):
    with tempfile.TemporaryDirectory() as tmp_dir:
        step_path = os.path.join(tmp_dir, "test_part.step")
        result_path = StepExporter.export_step(sample_solid, step_path)

        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 100  # STEP file contains geometry headers


def test_stl_export(sample_solid: cq.Workplane):
    with tempfile.TemporaryDirectory() as tmp_dir:
        stl_path = os.path.join(tmp_dir, "test_part.stl")
        result_path = StepExporter.export_stl(sample_solid, stl_path)

        assert os.path.exists(result_path)
        assert os.path.getsize(result_path) > 100


def test_step_roundtrip_verification(sample_solid: cq.Workplane):
    """
    Guarantees STEP roundtrip integrity:
    Model is exported to STEP, re-imported into OpenCascade, and checked for volumetric deviation.
    """
    passed, deviation_pct = StepExporter.verify_step_roundtrip(sample_solid)
    assert passed
    assert deviation_pct < 0.01  # Less than 0.01% deviation


def test_inspection_report_compiler(sample_solid: cq.Workplane):
    validator = GeometryValidator()
    spec = DrawingSpec(
        drawing_number="DWG-REP-01",
        title="Drive Flange",
        revision="B",
        material="Steel 4140",
        general_tolerance="ISO 2768-m",
        dimensions=[
            DimensionSpec(
                id="d_len",
                name="Overall Length",
                value=100.0,
                status=DimensionStatus.VERIFIED_AUTO,
            )
        ],
    )

    val_report = validator.validate(sample_solid, spec=spec)
    report_data = InspectionReportCompiler.compile_report_data(
        job_id="job_qa_123",
        spec=spec,
        validation=val_report,
        signed_off_by="Quality Assurance Chief",
        model_version=2,
    )

    assert report_data["job_id"] == "job_qa_123"
    assert report_data["drawing_number"] == "DWG-REP-01"
    assert report_data["overall_status"] == "APPROVED"
    assert report_data["sign_off"]["approver"] == "Quality Assurance Chief"
    assert report_data["sign_off"]["model_version"] == 2
    assert len(report_data["dimensions_table"]) > 0
