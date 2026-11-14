"""
Unit tests for the Engineering Sanity Rules Engine.
"""

import pytest
from sketch2step_spec.drawing import (
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
from sketch2step_spec.rules_engine import (
    check_dimension_positivity,
    check_tolerance_bounds,
    check_unit_consistency,
    check_overall_vs_segment_sums,
    check_hole_placement_and_margins,
    check_fillet_chamfer_proportions,
    check_iso_thread_standards,
    check_pattern_spacing_feasibility,
    run_all_sanity_checks,
)


def test_positive_dimensions_pass():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=100.0),
            DimensionSpec(id="d2", name="Width", value=50.0),
        ]
    )
    results = check_dimension_positivity(spec)
    assert len(results) == 1
    assert results[0].passed is True


def test_negative_or_zero_dimensions_fail():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=0.0),
            DimensionSpec(id="d2", name="Width", value=-5.0),
            DimensionSpec(id="d3", name="Valid", value=10.0),
        ]
    )
    results = check_dimension_positivity(spec)
    assert results[0].passed is False
    assert "d1" in results[0].affected_dimension_ids
    assert "d2" in results[0].affected_dimension_ids
    assert "d3" not in results[0].affected_dimension_ids


def test_tolerance_bounds_valid():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=100.0, tol_plus=0.1, tol_minus=0.05),
        ]
    )
    results = check_tolerance_bounds(spec)
    assert results[0].passed is True


def test_negative_tolerance_fails():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="BadTol", value=50.0, tol_plus=-0.1, tol_minus=0.0),
        ]
    )
    results = check_tolerance_bounds(spec)
    assert results[0].passed is False
    assert "d1" in results[0].affected_dimension_ids


def test_unit_consistency():
    spec = DrawingSpec(
        unit="mm",
        dimensions=[
            DimensionSpec(id="d1", name="L", value=100.0, unit="mm"),
            DimensionSpec(id="d2", name="W", value=5.0, unit="in"),
        ],
    )
    results = check_unit_consistency(spec)
    assert results[0].passed is False
    assert "d2" in results[0].affected_dimension_ids


def test_overall_length_matches_shaft_segments():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d_tot", name="Overall Length", value=120.0),
        ],
        features=[
            FeatureSpec(
                id="f_shaft",
                type=FeatureType.STEPPED_SHAFT,
                parameters={
                    "steps": [
                        {"diameter": 20.0, "length": 40.0},
                        {"diameter": 30.0, "length": 50.0},
                        {"diameter": 25.0, "length": 30.0},
                    ]
                },
            )
        ],
    )
    results = check_overall_vs_segment_sums(spec)
    assert results[0].passed is True


def test_overall_length_mismatch_shaft_segments():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d_tot", name="Overall Length", value=100.0),  # Sum is 40+50+30=120
        ],
        features=[
            FeatureSpec(
                id="f_shaft",
                type=FeatureType.STEPPED_SHAFT,
                dimension_ids=["d_s1", "d_s2", "d_s3"],
                parameters={
                    "steps": [
                        {"diameter": 20.0, "length": 40.0},
                        {"diameter": 30.0, "length": 50.0},
                        {"diameter": 25.0, "length": 30.0},
                    ]
                },
            )
        ],
    )
    results = check_overall_vs_segment_sums(spec)
    assert results[0].passed is False
    assert "d_tot" in results[0].affected_dimension_ids


def test_hole_within_plate_boundary_passes():
    spec = DrawingSpec(
        features=[
            FeatureSpec(
                id="f_base",
                type=FeatureType.PLATE,
                parameters={"length": 100.0, "width": 80.0, "thickness": 10.0},
            ),
            FeatureSpec(
                id="f_hole",
                type=FeatureType.HOLE_THROUGH,
                parameters={"diameter": 10.0, "x": 20.0, "y": 15.0},
            ),
        ]
    )
    results = check_hole_placement_and_margins(spec)
    assert results[0].passed is True


def test_hole_outside_plate_boundary_fails():
    spec = DrawingSpec(
        features=[
            FeatureSpec(
                id="f_base",
                type=FeatureType.PLATE,
                parameters={"length": 100.0, "width": 80.0, "thickness": 10.0},
            ),
            FeatureSpec(
                id="f_bad_hole",
                type=FeatureType.HOLE_THROUGH,
                dimension_ids=["d_h1"],
                parameters={"diameter": 20.0, "x": 45.0, "y": 0.0},  # 45 + 10 = 55 > half length 50
            ),
        ]
    )
    results = check_hole_placement_and_margins(spec)
    assert results[0].passed is False
    assert "d_h1" in results[0].affected_dimension_ids


def test_fillet_larger_than_thickness_fails():
    spec = DrawingSpec(
        features=[
            FeatureSpec(
                id="f_plate",
                type=FeatureType.PLATE,
                parameters={"length": 100.0, "width": 50.0, "thickness": 8.0},
            ),
            FeatureSpec(
                id="f_fillet",
                type=FeatureType.FILLET,
                dimension_ids=["d_fillet"],
                parameters={"radius": 10.0},  # 10 > thickness 8
            ),
        ]
    )
    results = check_fillet_chamfer_proportions(spec)
    assert results[0].passed is False
    assert "d_fillet" in results[0].affected_dimension_ids


def test_iso_thread_standard_checks():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d_t1", name="Thread M8", type=DimensionType.THREAD, value=8.0),
            DimensionSpec(id="d_t2", name="Thread M99", type=DimensionType.THREAD, value=99.0),
        ]
    )
    results = check_iso_thread_standards(spec)
    # d_t2 should fail standard ISO check
    assert any(not r.passed and "d_t2" in r.affected_dimension_ids for r in results)


def test_pattern_span_exceeds_host_fails():
    spec = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d_l", name="Overall Length", value=100.0),
        ],
        features=[
            FeatureSpec(
                id="f_pat",
                type=FeatureType.HOLE_PATTERN_LINEAR,
                dimension_ids=["d_l"],
                parameters={"count": 5, "pitch": 30.0},  # (5-1)*30 = 120 > 100
            )
        ],
    )
    results = check_pattern_spacing_feasibility(spec)
    assert results[0].passed is False
    assert "d_l" in results[0].affected_dimension_ids


def test_run_all_sanity_checks_clean_spec():
    spec = DrawingSpec(
        unit="mm",
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=100.0, tol_plus=0.1, tol_minus=0.1),
            DimensionSpec(id="d2", name="Width", value=50.0),
            DimensionSpec(id="d3", name="Thickness", value=10.0),
        ],
        features=[
            FeatureSpec(
                id="f_base",
                type=FeatureType.PLATE,
                parameters={"length": 100.0, "width": 50.0, "thickness": 10.0},
            ),
            FeatureSpec(
                id="f_fillet",
                type=FeatureType.FILLET,
                parameters={"radius": 2.0},
            ),
        ],
    )
    results = run_all_sanity_checks(spec)
    assert all(r.passed for r in results)
