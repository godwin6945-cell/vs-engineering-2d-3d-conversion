"""
Unit tests for AI Extraction module schema converters and tool definitions.
"""

from apps.worker.extraction import (
    EXTRACTION_TOOLS,
    _tool_input_to_dimension,
    _tool_input_to_feature,
)
from sketch2step_spec.enums import DimensionSource, DimensionStatus, DimensionType, FeatureType


def test_extraction_tools_structure():
    tool_names = [t["name"] for t in EXTRACTION_TOOLS]
    assert "record_dimension" in tool_names
    assert "record_feature" in tool_names
    assert "record_drawing_metadata" in tool_names


def test_tool_input_to_dimension():
    tool_data = {
        "id": "dim_01",
        "name": "Overall Width",
        "value": 150.0,
        "unit": "mm",
        "type": "linear",
        "source": "printed",
        "confidence": 0.95,
        "view": "front",
        "bbox_x_min": 0.1,
        "bbox_y_min": 0.2,
        "bbox_x_max": 0.3,
        "bbox_y_max": 0.25,
        "tol_plus": 0.2,
        "tol_minus": 0.1,
        "notes": "Title block reference",
    }
    dim = _tool_input_to_dimension(tool_data)
    assert dim.id == "dim_01"
    assert dim.value == 150.0
    assert dim.type == DimensionType.LINEAR
    assert dim.source == DimensionSource.PRINTED
    assert dim.confidence == 0.95
    assert dim.status == DimensionStatus.NEEDS_HUMAN  # Initial state prior to reconciliation
    assert dim.bbox is not None
    assert dim.bbox.x_min == 0.1
    assert dim.bbox.y_max == 0.25


def test_tool_input_to_feature():
    tool_data = {
        "id": "feat_hole_01",
        "type": "hole_through",
        "dimension_ids": ["dim_01", "dim_02"],
        "parameters": {"diameter": 12.0, "x": 30.0, "y": 20.0},
        "parent_feature_id": "feat_base_plate",
    }
    feat = _tool_input_to_feature(tool_data)
    assert feat.id == "feat_hole_01"
    assert feat.type == FeatureType.HOLE_THROUGH
    assert feat.dimension_ids == ["dim_01", "dim_02"]
    assert feat.parameters["diameter"] == 12.0
    assert feat.parent_feature_id == "feat_base_plate"
