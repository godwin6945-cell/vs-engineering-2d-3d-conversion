"""
Tests for DrawingSpec schema and accuracy verification invariants.
"""

import pytest
from sketch2step_spec.drawing import (
    BoundingBox,
    DimensionEvidence,
    DimensionSpec,
    DrawingSpec,
    FeatureSpec,
)
from sketch2step_spec.enums import (
    DimensionSource,
    DimensionStatus,
    DimensionType,
    FeatureType,
    ViewType,
)


def test_bounding_box_validation():
    # Valid box
    bbox = BoundingBox(x_min=0.1, y_min=0.2, x_max=0.5, y_max=0.6)
    assert bbox.x_max >= bbox.x_min
    assert bbox.y_max >= bbox.y_min

    # Invalid box where x_max < x_min
    with pytest.raises(ValueError):
        BoundingBox(x_min=0.8, y_min=0.2, x_max=0.3, y_max=0.6)


def test_accuracy_rule_blocks_unverified_dimensions():
    """
    Accuracy rule: No dimension reaches STEP unless verified by cross-check or confirmed by human.
    """
    dim1 = DimensionSpec(
        id="dim_01",
        name="Overall Length",
        value=100.0,
        unit="mm",
        status=DimensionStatus.VERIFIED_AUTO,
        evidence=DimensionEvidence(
            claude_pass_a=100.0,
            claude_pass_b=100.0,
            ocr_reading=100.0,
            agreement_score=1.0,
        ),
    )
    dim2 = DimensionSpec(
        id="dim_02",
        name="Hole Diameter",
        value=12.5,
        unit="mm",
        status=DimensionStatus.NEEDS_HUMAN,  # Unverified!
        evidence=DimensionEvidence(
            claude_pass_a=12.5,
            claude_pass_b=12.0,  # Discrepancy!
            ocr_reading=12.5,
            agreement_score=0.66,
        ),
    )

    spec = DrawingSpec(
        drawing_number="DWG-001",
        title="Flange Plate",
        unit="mm",
        dimensions=[dim1, dim2],
    )

    # Must NOT allow generation yet
    assert not spec.all_dimensions_verified
    assert len(spec.pending_human_dimensions) == 1
    assert spec.pending_human_dimensions[0].id == "dim_02"

    # Human confirms dim2
    dim2.status = DimensionStatus.HUMAN_CONFIRMED
    dim2.confirmed_by_user_id = "user_qa_lead"

    # Now all dimensions are verified
    assert spec.all_dimensions_verified
    assert len(spec.pending_human_dimensions) == 0
