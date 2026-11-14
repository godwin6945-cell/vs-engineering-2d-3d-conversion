"""
Unit tests for the Deterministic CAD Feature Compiler and Accuracy Invariants.
"""

import pytest
from sketch2step_cad.compiler import CompilationError, FeatureCompiler
from sketch2step_spec.drawing import DimensionSpec, DrawingSpec, FeatureSpec
from sketch2step_spec.enums import DimensionStatus, DimensionType, FeatureType


def test_compiler_accuracy_rule_blocks_unverified_dimensions():
    """Compiler must reject specifications where any dimension is unverified."""
    compiler = FeatureCompiler()

    dim1 = DimensionSpec(
        id="dim_len",
        name="Length",
        value=100.0,
        status=DimensionStatus.VERIFIED_AUTO,
    )
    dim2 = DimensionSpec(
        id="dim_wid",
        name="Width",
        value=50.0,
        status=DimensionStatus.NEEDS_HUMAN,  # Unverified!
    )

    feat = FeatureSpec(
        id="feat_plate",
        type=FeatureType.PLATE,
        dimension_ids=["dim_len", "dim_wid"],
        parameters={"length": "dim_len", "width": "dim_wid", "thickness": 10.0},
    )

    spec = DrawingSpec(
        drawing_number="DWG-TEST-01",
        dimensions=[dim1, dim2],
        features=[feat],
    )

    with pytest.raises(CompilationError, match="Accuracy Rule violation"):
        compiler.compile(spec)


def test_compiler_multi_feature_part():
    """Compiles multi-feature part: Base plate + Rectangular pocket + PCD hole pattern."""
    compiler = FeatureCompiler()

    # Confirmed dimensions
    dims = [
        DimensionSpec(id="d_len", name="Length", value=120.0, status=DimensionStatus.VERIFIED_AUTO),
        DimensionSpec(id="d_wid", name="Width", value=120.0, status=DimensionStatus.VERIFIED_AUTO),
        DimensionSpec(id="d_thk", name="Thickness", value=20.0, status=DimensionStatus.VERIFIED_AUTO),
        DimensionSpec(id="d_pcd", name="PCD", value=80.0, status=DimensionStatus.HUMAN_CONFIRMED),
        DimensionSpec(id="d_hdia", name="Hole Dia", value=10.0, status=DimensionStatus.HUMAN_ENTERED),
    ]

    features = [
        # 1. Base Plate
        FeatureSpec(
            id="f_plate",
            type=FeatureType.PLATE,
            dimension_ids=["d_len", "d_wid", "d_thk"],
            parameters={"length": "d_len", "width": "d_wid", "thickness": "d_thk"},
        ),
        # 2. Central Pocket
        FeatureSpec(
            id="f_pocket",
            type=FeatureType.POCKET_CIRCLE,
            parameters={"diameter": 40.0, "depth": 10.0, "x": 0.0, "y": 0.0},
        ),
        # 3. 4-hole Circular PCD Pattern
        FeatureSpec(
            id="f_pcd",
            type=FeatureType.HOLE_PATTERN_CIRCULAR,
            dimension_ids=["d_pcd", "d_hdia"],
            parameters={"pcd": "d_pcd", "count": 4, "diameter": "d_hdia"},
        ),
    ]

    spec = DrawingSpec(
        drawing_number="DWG-ASM-01",
        title="Mounting Flange Assembly",
        dimensions=dims,
        features=features,
    )

    solid = compiler.compile(spec)
    shape = solid.val()

    assert shape.isValid()
    # Confirm bounding box matches plate dimensions
    bb = shape.BoundingBox()
    assert round(bb.xlen, 1) == 120.0
    assert round(bb.ylen, 1) == 120.0
    assert round(bb.zlen, 1) == 20.0


def test_compiler_missing_base_feature():
    compiler = FeatureCompiler()
    dims = [DimensionSpec(id="d1", name="Dia", value=10.0, status=DimensionStatus.VERIFIED_AUTO)]
    # Only a hole feature, without a base solid
    features = [FeatureSpec(id="f1", type=FeatureType.HOLE_THROUGH, parameters={"diameter": 10.0})]

    spec = DrawingSpec(dimensions=dims, features=features)
    with pytest.raises(CompilationError, match="must define at least one base structural feature"):
        compiler.compile(spec)


def test_compiler_parameter_injection():
    """Verify that dimension IDs in parameters are dynamically injected with their numeric value."""
    compiler = FeatureCompiler()
    dims = [
        DimensionSpec(id="d_dia", name="Diameter", value=50.0, status=DimensionStatus.VERIFIED_AUTO),
        DimensionSpec(id="d_h", name="Height", value=75.0, status=DimensionStatus.VERIFIED_AUTO),
    ]
    features = [
        FeatureSpec(
            id="f_cyl",
            type=FeatureType.CYLINDER,
            dimension_ids=["d_dia", "d_h"],
            parameters={"diameter": "d_dia", "height": "d_h"},
        )
    ]
    spec = DrawingSpec(dimensions=dims, features=features)
    solid = compiler.compile(spec)

    bb = solid.val().BoundingBox()
    assert round(bb.xlen, 1) == 50.0
    assert round(bb.zlen, 1) == 75.0
