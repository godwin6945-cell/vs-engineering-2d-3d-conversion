"""
Unit tests for the Reconciliation Engine.
Verifies the core accuracy rules:
- All three agree (Pass A + Pass B + OCR) + printed -> verified_auto
- Any disagreement, inferred value, or missing value -> needs_human
"""

import pytest
from sketch2step_spec.drawing import (
    BoundingBox,
    DimensionSpec,
    DrawingSpec,
    FeatureSpec,
)
from sketch2step_spec.enums import (
    DimensionSource,
    DimensionStatus,
    DimensionType,
    FeatureType,
)
from apps.worker.reconciliation import (
    compute_agreement,
    reconcile_dimensions,
    reconcile_drawing_specs,
    values_agree,
)


def test_values_agree():
    assert values_agree(100.0, 100.0) is True
    assert values_agree(100.0, 100.04) is True  # within 0.05 default tol
    assert values_agree(100.0, 100.1) is False
    assert values_agree(None, 100.0) is False


def test_compute_agreement_triple_match():
    score, val, is_triple = compute_agreement(50.0, 50.0, 50.0)
    assert score == 1.0
    assert val == 50.0
    assert is_triple is True


def test_compute_agreement_pass_ab_only():
    score, val, is_triple = compute_agreement(50.0, 50.0, None)
    assert score == 0.67
    assert val == 50.0
    assert is_triple is False


def test_compute_agreement_disagreement():
    score, val, is_triple = compute_agreement(50.0, 60.0, 70.0)
    assert score == 0.0
    assert is_triple is False


def test_reconciliation_triple_agreement_verified_auto():
    """When Pass A, Pass B, and OCR agree on a printed dimension, status is verified_auto."""
    dim_a = DimensionSpec(
        id="d1",
        name="Length",
        value=100.0,
        source=DimensionSource.PRINTED,
        bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.2),
    )
    dim_b = DimensionSpec(
        id="d1",
        name="Length",
        value=100.0,
        source=DimensionSource.PRINTED,
    )
    ocr_matches = {"d1": 100.0}

    reconciled = reconcile_dimensions([dim_a], [dim_b], ocr_matches)

    assert len(reconciled) == 1
    d = reconciled[0]
    assert d.status == DimensionStatus.VERIFIED_AUTO
    assert d.is_verified is True
    assert d.value == 100.0
    assert d.evidence is not None
    assert d.evidence.agreement_score == 1.0
    assert d.evidence.claude_pass_a == 100.0
    assert d.evidence.claude_pass_b == 100.0
    assert d.evidence.ocr_reading == 100.0


def test_reconciliation_disagreement_needs_human():
    """Disagreement between Pass A (100) and Pass B (102) blocks auto-verification."""
    dim_a = DimensionSpec(id="d1", name="Length", value=100.0, source=DimensionSource.PRINTED)
    dim_b = DimensionSpec(id="d1", name="Length", value=102.0, source=DimensionSource.PRINTED)
    ocr_matches = {"d1": 100.0}

    reconciled = reconcile_dimensions([dim_a], [dim_b], ocr_matches)

    assert len(reconciled) == 1
    d = reconciled[0]
    assert d.status == DimensionStatus.NEEDS_HUMAN
    assert d.is_verified is False
    assert "Discrepancy" in (d.notes or "")


def test_reconciliation_inferred_dimension_needs_human():
    """Inferred dimension must require human review even if all three readings match."""
    dim_a = DimensionSpec(id="d1", name="Length", value=100.0, source=DimensionSource.INFERRED)
    dim_b = DimensionSpec(id="d1", name="Length", value=100.0, source=DimensionSource.INFERRED)
    ocr_matches = {"d1": 100.0}

    reconciled = reconcile_dimensions([dim_a], [dim_b], ocr_matches)

    d = reconciled[0]
    assert d.status == DimensionStatus.NEEDS_HUMAN
    assert d.is_verified is False


def test_reconciliation_missing_dimension_needs_human():
    """Missing dimension (None value) must require human input."""
    dim_a = DimensionSpec(id="d1", name="Length", value=None, source=DimensionSource.MISSING)
    dim_b = DimensionSpec(id="d1", name="Length", value=None, source=DimensionSource.MISSING)
    ocr_matches = {"d1": None}

    reconciled = reconcile_dimensions([dim_a], [dim_b], ocr_matches)

    d = reconciled[0]
    assert d.status == DimensionStatus.NEEDS_HUMAN
    assert d.is_verified is False
    assert d.value is None


def test_reconciliation_single_pass_only_needs_human():
    """Dimension found only in Pass B is preserved but flagged needs_human."""
    dim_a = DimensionSpec(id="d1", name="Length", value=100.0, source=DimensionSource.PRINTED)
    dim_b1 = DimensionSpec(id="d1", name="Length", value=100.0, source=DimensionSource.PRINTED)
    dim_b2 = DimensionSpec(id="d2", name="Extra Width", value=50.0, source=DimensionSource.PRINTED)

    reconciled = reconcile_dimensions([dim_a], [dim_b1, dim_b2], {"d1": 100.0})

    assert len(reconciled) == 2
    d2 = next(d for d in reconciled if d.id == "d2")
    assert d2.status == DimensionStatus.NEEDS_HUMAN
    assert d2.value == 50.0


def test_master_reconciliation_full_pipeline():
    """Full DrawingSpec reconciliation merging features, notes, and sanity checks."""
    spec_a = DrawingSpec(
        title="Base Plate",
        unit="mm",
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=120.0, source=DimensionSource.PRINTED),
            DimensionSpec(id="d2", name="Width", value=80.0, source=DimensionSource.PRINTED),
            DimensionSpec(id="d3", name="Thickness", value=12.0, source=DimensionSource.PRINTED),
        ],
        features=[
            FeatureSpec(
                id="f_plate",
                type=FeatureType.PLATE,
                dimension_ids=["d1", "d2", "d3"],
                parameters={"length": 120.0, "width": 80.0, "thickness": 12.0},
            )
        ],
        notes=["General tolerance ISO 2768-m"],
    )

    spec_b = DrawingSpec(
        title="Base Plate",
        unit="mm",
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=120.0, source=DimensionSource.PRINTED),
            DimensionSpec(id="d2", name="Width", value=80.0, source=DimensionSource.PRINTED),
            DimensionSpec(id="d3", name="Thickness", value=12.0, source=DimensionSource.PRINTED),
        ],
        features=[
            FeatureSpec(
                id="f_plate",
                type=FeatureType.PLATE,
                dimension_ids=["d1", "d2", "d3"],
                parameters={"length": 120.0, "width": 80.0, "thickness": 12.0},
            )
        ],
        notes=["Material: Steel 1018"],
    )

    ocr_matches = {"d1": 120.0, "d2": 80.0, "d3": 12.0}

    final_spec = reconcile_drawing_specs(spec_a, spec_b, ocr_matches)

    assert final_spec.title == "Base Plate"
    assert len(final_spec.dimensions) == 3
    assert final_spec.all_dimensions_verified is True
    assert len(final_spec.pending_human_dimensions) == 0
    assert len(final_spec.features) == 1
    assert "General tolerance ISO 2768-m" in final_spec.notes
    assert "Material: Steel 1018" in final_spec.notes
    assert len(final_spec.sanity_checks) > 0
    assert all(sc.passed for sc in final_spec.sanity_checks)
