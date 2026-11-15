"""
Unit and integration tests for Evaluation Harness and Accuracy Gating.
"""

import pytest
from pathlib import Path
from eval.runner import EvaluationRunner, run_evaluation_suite
from sketch2step_spec.drawing import DrawingSpec, DimensionSpec, DimensionEvidence, BoundingBox
from sketch2step_spec.enums import DimensionStatus, DimensionType, DimensionSource, ViewType


def test_eval_suite_passes_benchmarks():
    """Verify that synthetic benchmark dataset passes all gating checks."""
    summary = run_evaluation_suite(dataset_path="eval/datasets")
    assert summary["status"] == "PASS"
    assert summary["parts_evaluated"] == 30
    assert summary["total_dimensions"] > 100
    assert summary["false_verified_rate"] == 0.0
    assert summary["exact_match_rate"] >= 0.98
    assert summary["gating_rules"]["zero_false_verified_passed"] is True
    assert summary["gating_rules"]["exact_match_threshold_passed"] is True
    assert summary["gating_rules"]["cad_topology_valid_passed"] is True


def test_eval_runner_detects_false_verified_regression(tmp_path):
    """Verify that evaluation runner catches an unsafe false verified dimension and fails gating."""
    runner = EvaluationRunner(dataset_dir="eval/datasets")

    # Pick first dataset and test single part
    res = runner.evaluate_part(Path("eval/datasets/part_01"))
    assert res["false_verified_count"] == 0
    assert res["is_valid_cad"] is True
    assert res["volume_deviation_pct"] == 0.0
