"""
Unit tests for structural CAD builders: Flanges, L-Brackets, U-Brackets.
"""

import math
import pytest
from sketch2step_cad.builders.structural import (
    BracketLBuilder,
    BracketUBuilder,
    FlangeBuilder,
)


def test_flange_builder_flat_disc():
    builder = FlangeBuilder()
    solid = builder.build(outer_diameter=100.0, thickness=12.0)

    shape = solid.val()
    assert shape.isValid()
    expected_vol = math.pi * (50.0 ** 2) * 12.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 100.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 12.0, rel_tol=1e-3)


def test_flange_builder_with_bore_and_hub():
    builder = FlangeBuilder()
    solid = builder.build(
        outer_diameter=120.0,
        thickness=15.0,
        bore_diameter=40.0,
        hub_diameter=70.0,
        hub_height=25.0,
    )

    shape = solid.val()
    assert shape.isValid()
    # Base disc: pi * 60^2 * 15
    # Hub: pi * 35^2 * 25
    # Through bore: - pi * 20^2 * 40
    expected_vol = (
        math.pi * (60.0 ** 2) * 15.0
        + math.pi * (35.0 ** 2) * 25.0
        - math.pi * (20.0 ** 2) * 40.0
    )
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_bracket_l_builder_dimensions():
    builder = BracketLBuilder()
    solid = builder.build(leg1=60.0, leg2=80.0, width=40.0, thickness=8.0)

    shape = solid.val()
    assert shape.isValid()
    # Cross sectional area = (60 * 8) + (80 - 8) * 8 = 480 + 576 = 1056 mm2
    # Volume = area * width = 1056 * 40 = 42240 mm3
    expected_vol = (60.0 * 8.0 + (80.0 - 8.0) * 8.0) * 40.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)

    bb = shape.BoundingBox()
    assert math.isclose(bb.xlen, 60.0, rel_tol=1e-3)
    assert math.isclose(bb.ylen, 40.0, rel_tol=1e-3)
    assert math.isclose(bb.zlen, 80.0, rel_tol=1e-3)


def test_bracket_l_builder_invalid_thickness():
    builder = BracketLBuilder()
    with pytest.raises(ValueError, match="must be less than leg1"):
        builder.build(leg1=30.0, leg2=40.0, width=20.0, thickness=35.0)


def test_bracket_u_builder_dimensions():
    builder = BracketUBuilder()
    solid = builder.build(base_width=100.0, leg_height=50.0, length=60.0, thickness=10.0)

    shape = solid.val()
    assert shape.isValid()
    # Profile area = (base_width * thickness) + 2 * (leg_height - thickness) * thickness
    # = (100 * 10) + 2 * (40 * 10) = 1000 + 800 = 1800 mm2
    # Volume = 1800 * 60 = 108000 mm3
    expected_vol = (100.0 * 10.0 + 2.0 * (50.0 - 10.0) * 10.0) * 60.0
    assert math.isclose(shape.Volume(), expected_vol, rel_tol=1e-3)


def test_bracket_u_builder_exceeding_thickness():
    builder = BracketUBuilder()
    with pytest.raises(ValueError, match="exceeds physical boundaries"):
        builder.build(base_width=50.0, leg_height=40.0, length=30.0, thickness=26.0)
