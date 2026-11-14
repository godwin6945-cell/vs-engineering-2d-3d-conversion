"""
Unit tests for the Spec & Geometry Diff engine.
"""

import pytest
from sketch2step_spec.diff import (
    compute_geometry_diff,
    compute_spec_diff,
)
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec
from sketch2step_spec.enums import DimensionStatus
from sketch2step_spec.job import ValidationReport


def test_compute_spec_diff_detects_changes():
    spec_v1 = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=100.0, status=DimensionStatus.VERIFIED_AUTO),
            DimensionSpec(id="d2", name="Width", value=50.0, status=DimensionStatus.VERIFIED_AUTO),
            DimensionSpec(id="d3", name="RemoveMe", value=10.0, status=DimensionStatus.VERIFIED_AUTO),
        ]
    )

    spec_v2 = DrawingSpec(
        dimensions=[
            DimensionSpec(id="d1", name="Length", value=100.0, status=DimensionStatus.VERIFIED_AUTO), # Unchanged
            DimensionSpec(id="d2", name="Width", value=55.0, status=DimensionStatus.HUMAN_CONFIRMED), # Modified value & status
            DimensionSpec(id="d4", name="NewHole", value=8.0, status=DimensionStatus.HUMAN_CONFIRMED), # Added
        ]
    )

    changes = compute_spec_diff(spec_v1, spec_v2)
    change_map = {c.dimension_id: c for c in changes}

    assert change_map["d1"].change_type == "UNCHANGED"
    assert change_map["d2"].change_type == "MODIFIED"
    assert change_map["d2"].old_value == 50.0
    assert change_map["d2"].new_value == 55.0
    assert change_map["d2"].value_delta == 5.0
    assert change_map["d3"].change_type == "REMOVED"
    assert change_map["d4"].change_type == "ADDED"
    assert change_map["d4"].new_value == 8.0


def test_compute_geometry_diff():
    rep_v1 = ValidationReport(
        is_valid_solid=True,
        is_shell_closed=True,
        has_self_intersections=False,
        bounding_box_x=100.0,
        bounding_box_y=50.0,
        bounding_box_z=20.0,
        volume_mm3=100000.0,
        surface_area_mm2=20000.0,
        face_count=6,
        edge_count=12,
        hole_count=0,
        step_roundtrip_ok=True,
        overall_passed=True,
    )

    rep_v2 = ValidationReport(
        is_valid_solid=True,
        is_shell_closed=True,
        has_self_intersections=False,
        bounding_box_x=100.0,
        bounding_box_y=55.0,
        bounding_box_z=20.0,
        volume_mm3=110000.0,
        surface_area_mm2=21500.0,
        face_count=7,
        edge_count=15,
        hole_count=1,
        step_roundtrip_ok=True,
        overall_passed=True,
    )

    geo_diff = compute_geometry_diff(rep_v1, rep_v2)
    assert geo_diff is not None
    assert geo_diff.volume_delta_mm3 == 10000.0
    assert geo_diff.bounding_box_delta_y == 5.0
    assert geo_diff.face_count_delta == 1
