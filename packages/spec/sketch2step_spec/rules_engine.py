"""
Engineering Sanity Rules Engine.
Pure Python validation checks verifying dimensional integrity, geometric feasibility,
and ISO standard compliance before human sign-off or CAD synthesis.
"""

import re
from typing import Dict, List, Optional
from .drawing import DrawingSanityCheckResult, DrawingSpec
from .enums import DimensionType, FeatureType

# ISO Metric Coarse Pitch and Nominal Diameters (ISO 261 / DIN 13)
ISO_METRIC_THREADS: Dict[str, float] = {
    "M1.6": 0.35,
    "M2": 0.4,
    "M2.5": 0.45,
    "M3": 0.5,
    "M4": 0.7,
    "M5": 0.8,
    "M6": 1.0,
    "M8": 1.25,
    "M10": 1.5,
    "M12": 1.75,
    "M14": 2.0,
    "M16": 2.0,
    "M18": 2.5,
    "M20": 2.5,
    "M22": 2.5,
    "M24": 3.0,
    "M27": 3.0,
    "M30": 3.5,
    "M36": 4.0,
}


def check_dimension_positivity(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 001: Dimensions must be positive non-zero physical numbers (except angles/coordinates)."""
    results: List[DrawingSanityCheckResult] = []
    invalid_ids = []

    for dim in spec.dimensions:
        if dim.value is not None and dim.type != DimensionType.ANGLE:
            if dim.value <= 0:
                invalid_ids.append(dim.id)

    if invalid_ids:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-001-POSITIVE-VAL",
                passed=False,
                severity="ERROR",
                message=f"Dimensions have non-positive values: {', '.join(invalid_ids)}",
                affected_dimension_ids=invalid_ids,
            )
        )
    else:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-001-POSITIVE-VAL",
                passed=True,
                severity="INFO",
                message="All physical dimension values are strictly positive.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_tolerance_bounds(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 002: Tolerance band must be well-formed (+tol >= 0, -tol >= 0)."""
    results: List[DrawingSanityCheckResult] = []
    invalid_ids = []

    for dim in spec.dimensions:
        if dim.tol_plus < 0 or dim.tol_minus < 0:
            invalid_ids.append(dim.id)

    if invalid_ids:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-002-TOLERANCE-VALID",
                passed=False,
                severity="ERROR",
                message=f"Negative tolerance specification found on dimensions: {', '.join(invalid_ids)}",
                affected_dimension_ids=invalid_ids,
            )
        )
    else:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-002-TOLERANCE-VALID",
                passed=True,
                severity="INFO",
                message="All tolerance specifications are valid positive bounds.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_unit_consistency(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 003: All linear dimensions must use consistent units matching drawing unit."""
    results: List[DrawingSanityCheckResult] = []
    expected_unit = spec.unit.lower()
    mismatched_ids = []

    for dim in spec.dimensions:
        if dim.type != DimensionType.ANGLE and dim.unit.lower() != expected_unit:
            mismatched_ids.append(dim.id)

    if mismatched_ids:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-003-UNIT-CONSISTENCY",
                passed=False,
                severity="WARNING",
                message=f"Dimensions unit mismatch (expected '{expected_unit}'): {', '.join(mismatched_ids)}",
                affected_dimension_ids=mismatched_ids,
            )
        )
    else:
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-003-UNIT-CONSISTENCY",
                passed=True,
                severity="INFO",
                message=f"All dimensions consistently specified in {expected_unit}.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_overall_vs_segment_sums(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """
    Rule 004: Overall length should equal the sum of segments along the same axis.
    Detects dimensions named 'Overall Length' or 'Total Length' vs segments.
    """
    results: List[DrawingSanityCheckResult] = []
    dim_map = {d.id: d for d in spec.dimensions}

    # Check stepped shaft features
    for feat in spec.features:
        if feat.type == FeatureType.STEPPED_SHAFT:
            steps = feat.parameters.get("steps", [])
            overall_len_param = feat.parameters.get("total_length")
            if steps:
                sum_step_lengths = sum(float(s.get("length", 0.0)) for s in steps)
                # Find matching overall dimension if present
                for d in spec.dimensions:
                    if "overall" in d.name.lower() and "length" in d.name.lower() and d.value is not None:
                        diff = abs(d.value - sum_step_lengths)
                        if diff > 0.05:  # tolerance 0.05mm
                            results.append(
                                DrawingSanityCheckResult(
                                    rule_id="SANITY-004-SUM-OF-SEGMENTS",
                                    passed=False,
                                    severity="ERROR",
                                    message=(
                                        f"Overall length {d.value} mm does not match sum of shaft segments "
                                        f"({sum_step_lengths:.2f} mm, diff: {diff:.3f} mm)"
                                    ),
                                    affected_dimension_ids=[d.id] + feat.dimension_ids,
                                )
                            )
                            return results

    results.append(
        DrawingSanityCheckResult(
            rule_id="SANITY-004-SUM-OF-SEGMENTS",
            passed=True,
            severity="INFO",
            message="Overall length and segmental sums are consistent.",
            affected_dimension_ids=[],
        )
    )
    return results


def check_hole_placement_and_margins(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """
    Rule 005: Holes must be placed inside part boundaries and have positive edge margins.
    """
    results: List[DrawingSanityCheckResult] = []
    # Find base feature bounding dimensions
    base_feats = [
        f for f in spec.features
        if f.type in (FeatureType.PLATE, FeatureType.BLOCK, FeatureType.FLANGE)
    ]
    if not base_feats:
        return results

    base = base_feats[0]
    base_length = float(base.parameters.get("length", 0.0))
    base_width = float(base.parameters.get("width", 0.0))
    base_dia = float(base.parameters.get("diameter", base.parameters.get("outer_diameter", 0.0)))

    for feat in spec.features:
        if feat.type in (
            FeatureType.HOLE_THROUGH,
            FeatureType.HOLE_BLIND,
            FeatureType.HOLE_COUNTERBORE,
            FeatureType.HOLE_COUNTERSINK,
        ):
            dia = float(feat.parameters.get("diameter", 0.0))
            x = float(feat.parameters.get("x", 0.0))
            y = float(feat.parameters.get("y", 0.0))
            radius = dia / 2.0

            if base_length > 0 and base_width > 0:
                # Assuming centered box from -L/2 to +L/2, -W/2 to +W/2
                half_l = base_length / 2.0
                half_w = base_width / 2.0
                margin_x = half_l - (abs(x) + radius)
                margin_y = half_w - (abs(y) + radius)

                if margin_x < 0 or margin_y < 0:
                    results.append(
                        DrawingSanityCheckResult(
                            rule_id="SANITY-005-HOLE-BOUNDARY",
                            passed=False,
                            severity="ERROR",
                            message=(
                                f"Hole {feat.id} (dia={dia}) extends beyond part boundary "
                                f"(margin_x={margin_x:.2f}, margin_y={margin_y:.2f})"
                            ),
                            affected_dimension_ids=feat.dimension_ids,
                        )
                    )
            elif base_dia > 0:
                # Flange / circular base
                base_radius = base_dia / 2.0
                dist_from_center = (x**2 + y**2) ** 0.5
                margin = base_radius - (dist_from_center + radius)
                if margin < 0:
                    results.append(
                        DrawingSanityCheckResult(
                            rule_id="SANITY-005-HOLE-BOUNDARY",
                            passed=False,
                            severity="ERROR",
                            message=(
                                f"Hole {feat.id} extends outside circular boundary "
                                f"(edge margin={margin:.2f} mm)"
                            ),
                            affected_dimension_ids=feat.dimension_ids,
                        )
                    )

    if not any(not r.passed for r in results):
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-005-HOLE-BOUNDARY",
                passed=True,
                severity="INFO",
                message="All hole placements maintain safe boundary margins.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_fillet_chamfer_proportions(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 006: Fillet and chamfer sizes must not exceed feature thickness."""
    results: List[DrawingSanityCheckResult] = []
    base_feats = [
        f for f in spec.features
        if f.type in (FeatureType.PLATE, FeatureType.BLOCK, FeatureType.CYLINDER)
    ]
    min_thickness = float("inf")
    for bf in base_feats:
        t = float(bf.parameters.get("thickness", bf.parameters.get("height", 0.0)))
        if t > 0 and t < min_thickness:
            min_thickness = t

    for feat in spec.features:
        if feat.type in (FeatureType.FILLET, FeatureType.CHAMFER):
            size = float(feat.parameters.get("radius", feat.parameters.get("size", 0.0)))
            if min_thickness < float("inf") and size >= min_thickness:
                results.append(
                    DrawingSanityCheckResult(
                        rule_id="SANITY-006-DRESSUP-PROPORTIONS",
                        passed=False,
                        severity="ERROR",
                        message=(
                            f"{feat.type.value} {feat.id} size ({size} mm) exceeds or equals "
                            f"part thickness ({min_thickness} mm)"
                        ),
                        affected_dimension_ids=feat.dimension_ids,
                    )
                )

    if not any(not r.passed for r in results):
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-006-DRESSUP-PROPORTIONS",
                passed=True,
                severity="INFO",
                message="Fillet and chamfer proportions are within physical limits.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_iso_thread_standards(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 007: Thread callouts must conform to standard ISO metric thread profiles."""
    results: List[DrawingSanityCheckResult] = []
    thread_pattern = re.compile(r"\bM(\d+(?:\.\d+)?)(?:[xX](\d+(?:\.\d+)?))?\b", re.IGNORECASE)

    for dim in spec.dimensions:
        if dim.type == DimensionType.THREAD or "thread" in dim.name.lower():
            # Check name or notes for standard ISO callout
            target_str = dim.name
            if dim.notes:
                target_str += f" {dim.notes}"

            match = thread_pattern.search(target_str)
            if match:
                dia_str = f"M{match.group(1)}"
                if dia_str in ISO_METRIC_THREADS:
                    pitch_expected = ISO_METRIC_THREADS[dia_str]
                    if match.group(2):
                        pitch_given = float(match.group(2))
                        # Fine pitch or coarse pitch allowed, but pitch cannot be greater than nominal diameter
                        if pitch_given > float(match.group(1)) * 0.5:
                            results.append(
                                DrawingSanityCheckResult(
                                    rule_id="SANITY-007-ISO-THREAD",
                                    passed=False,
                                    severity="WARNING",
                                    message=f"Thread {dia_str} has abnormal pitch {pitch_given} mm (standard coarse is {pitch_expected} mm)",
                                    affected_dimension_ids=[dim.id],
                                )
                            )
                else:
                    results.append(
                        DrawingSanityCheckResult(
                            rule_id="SANITY-007-ISO-THREAD",
                            passed=False,
                            severity="WARNING",
                            message=f"Thread callout {dia_str} is not a standard ISO metric size",
                            affected_dimension_ids=[dim.id],
                        )
                    )

    if not any(not r.passed for r in results):
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-007-ISO-THREAD",
                passed=True,
                severity="INFO",
                message="Thread callouts conform to ISO metric standards.",
                affected_dimension_ids=[],
            )
        )
    return results


def check_pattern_spacing_feasibility(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """Rule 008: Pattern count and pitch spacing must fit within host dimension."""
    results: List[DrawingSanityCheckResult] = []

    for feat in spec.features:
        if feat.type == FeatureType.HOLE_PATTERN_LINEAR:
            count = int(feat.parameters.get("count", 1))
            pitch = float(feat.parameters.get("pitch", 0.0))
            span = (count - 1) * pitch

            # Check if any host feature bounding dimension is smaller than span
            for dim in spec.dimensions:
                if dim.id in feat.dimension_ids and dim.value is not None:
                    if dim.name.lower().startswith("overall") and dim.value < span:
                        results.append(
                            DrawingSanityCheckResult(
                                rule_id="SANITY-008-PATTERN-SPAN",
                                passed=False,
                                severity="ERROR",
                                message=(
                                    f"Linear pattern {feat.id} total span ({span} mm) exceeds "
                                    f"host dimension {dim.name} ({dim.value} mm)"
                                ),
                                affected_dimension_ids=[dim.id],
                            )
                        )

    if not any(not r.passed for r in results):
        results.append(
            DrawingSanityCheckResult(
                rule_id="SANITY-008-PATTERN-SPAN",
                passed=True,
                severity="INFO",
                message="Hole pattern layouts fit within host dimensions.",
                affected_dimension_ids=[],
            )
        )
    return results


def run_all_sanity_checks(spec: DrawingSpec) -> List[DrawingSanityCheckResult]:
    """
    Run complete suite of engineering sanity checks on a DrawingSpec.
    Returns list of DrawingSanityCheckResult objects.
    """
    all_results: List[DrawingSanityCheckResult] = []
    all_results.extend(check_dimension_positivity(spec))
    all_results.extend(check_tolerance_bounds(spec))
    all_results.extend(check_unit_consistency(spec))
    all_results.extend(check_overall_vs_segment_sums(spec))
    all_results.extend(check_hole_placement_and_margins(spec))
    all_results.extend(check_fillet_chamfer_proportions(spec))
    all_results.extend(check_iso_thread_standards(spec))
    all_results.extend(check_pattern_spacing_feasibility(spec))
    return all_results
