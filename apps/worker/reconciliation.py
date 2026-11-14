"""
Phase 3 – Reconciliation Engine.
Reconciles dimension readings across Claude Pass A, Claude Pass B, and RapidOCR.
Enforces the core accuracy rule:
- All three agree + value printed -> verified_auto
- Any disagreement, inferred value, or missing value -> needs_human
Runs engineering sanity checks on reconciled DrawingSpec.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

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
)
from sketch2step_spec.rules_engine import run_all_sanity_checks

logger = logging.getLogger(__name__)

# Numerical tolerance for dimension equality (e.g., 0.05 mm)
DEFAULT_COMPARISON_TOLERANCE = 0.05


def values_agree(
    v1: Optional[float],
    v2: Optional[float],
    tol: float = DEFAULT_COMPARISON_TOLERANCE,
) -> bool:
    """Check if two numeric readings agree within tolerance."""
    if v1 is None or v2 is None:
        return False
    return abs(v1 - v2) <= tol


def compute_agreement(
    val_a: Optional[float],
    val_b: Optional[float],
    val_ocr: Optional[float],
    tol: float = DEFAULT_COMPARISON_TOLERANCE,
) -> Tuple[float, Optional[float], bool]:
    """
    Compute agreement score (0.0 to 1.0), consensus value, and triple agreement flag.
    Returns (agreement_score, consensus_value, is_triple_agreement).
    """
    readings = [v for v in (val_a, val_b, val_ocr) if v is not None]
    if not readings:
        return 0.0, None, False

    match_ab = values_agree(val_a, val_b, tol)
    match_ao = values_agree(val_a, val_ocr, tol)
    match_bo = values_agree(val_b, val_ocr, tol)

    if match_ab and match_ao and match_bo:
        # All three agree
        return 1.0, val_a, True
    elif match_ab:
        # Pass A and Pass B agree, OCR disagrees or absent
        return 0.67, val_a, False
    elif match_ao:
        # Pass A and OCR agree, Pass B disagrees or absent
        return 0.67, val_a, False
    elif match_bo:
        # Pass B and OCR agree, Pass A disagrees or absent
        return 0.67, val_b, False
    else:
        # Total disagreement
        return 0.33 if len(readings) == 1 else 0.0, readings[0], False


def reconcile_dimensions(
    pass_a_dims: List[DimensionSpec],
    pass_b_dims: List[DimensionSpec],
    ocr_matches: Dict[str, Optional[float]],
    ocr_raw_text: Optional[Dict[str, str]] = None,
    tolerance: float = DEFAULT_COMPARISON_TOLERANCE,
) -> List[DimensionSpec]:
    """
    Reconcile dimensions from Pass A, Pass B, and OCR.
    """
    ocr_raw_text = ocr_raw_text or {}
    reconciled: List[DimensionSpec] = []

    # Map Pass B dimensions by ID and normalized name for robust matching
    b_by_id: Dict[str, DimensionSpec] = {d.id: d for d in pass_b_dims}
    b_by_name: Dict[str, DimensionSpec] = {d.name.strip().lower(): d for d in pass_b_dims}
    used_b_ids = set()

    for dim_a in pass_a_dims:
        # Find corresponding dim in Pass B
        dim_b = b_by_id.get(dim_a.id)
        if dim_b is None:
            dim_b = b_by_name.get(dim_a.name.strip().lower())

        if dim_b is not None:
            used_b_ids.add(dim_b.id)

        val_a = dim_a.value
        val_b = dim_b.value if dim_b else None
        val_ocr = ocr_matches.get(dim_a.id)
        if val_ocr is None and dim_b:
            val_ocr = ocr_matches.get(dim_b.id)

        agreement_score, consensus_val, triple_agreed = compute_agreement(
            val_a, val_b, val_ocr, tol=tolerance
        )

        evidence = DimensionEvidence(
            claude_pass_a=val_a,
            claude_pass_b=val_b,
            ocr_reading=val_ocr,
            agreement_score=agreement_score,
            raw_ocr_text=ocr_raw_text.get(dim_a.id),
        )

        # Enforce accuracy rule
        is_printed = (
            dim_a.source == DimensionSource.PRINTED
            and (dim_b is None or dim_b.source == DimensionSource.PRINTED)
        )

        if triple_agreed and is_printed and consensus_val is not None:
            status = DimensionStatus.VERIFIED_AUTO
            final_val = consensus_val
            conf = 1.0
            notes = dim_a.notes or (dim_b.notes if dim_b else None)
        else:
            status = DimensionStatus.NEEDS_HUMAN
            final_val = consensus_val if consensus_val is not None else val_a
            conf = min(dim_a.confidence, (dim_b.confidence if dim_b else 1.0))
            # Build explanatory notes for discrepancies
            reasons = []
            if not triple_agreed:
                reasons.append(
                    f"Discrepancy (Pass A: {val_a}, Pass B: {val_b}, OCR: {val_ocr})"
                )
            if not is_printed:
                reasons.append(f"Source not printed (Pass A: {dim_a.source.value})")
            if final_val is None:
                reasons.append("Missing value")
            notes = "; ".join(reasons)
            if dim_a.notes:
                notes = f"{notes} | {dim_a.notes}"

        # Prefer bbox from Pass A, fallback to Pass B
        bbox = dim_a.bbox or (dim_b.bbox if dim_b else None)

        reconciled.append(
            DimensionSpec(
                id=dim_a.id,
                name=dim_a.name,
                value=final_val,
                unit=dim_a.unit,
                tol_plus=dim_a.tol_plus,
                tol_minus=dim_a.tol_minus,
                type=dim_a.type,
                source=dim_a.source if is_printed else (DimensionSource.INFERRED if final_val is not None else DimensionSource.MISSING),
                confidence=conf,
                bbox=bbox,
                view=dim_a.view,
                status=status,
                evidence=evidence,
                notes=notes,
            )
        )

    # Check any leftover dimensions present only in Pass B
    for dim_b in pass_b_dims:
        if dim_b.id not in used_b_ids and dim_b.name.strip().lower() not in [d.name.strip().lower() for d in reconciled]:
            val_ocr = ocr_matches.get(dim_b.id)
            evidence = DimensionEvidence(
                claude_pass_a=None,
                claude_pass_b=dim_b.value,
                ocr_reading=val_ocr,
                agreement_score=0.33 if (val_ocr is None or not values_agree(dim_b.value, val_ocr)) else 0.67,
                raw_ocr_text=ocr_raw_text.get(dim_b.id),
            )
            reconciled.append(
                DimensionSpec(
                    id=dim_b.id,
                    name=dim_b.name,
                    value=dim_b.value,
                    unit=dim_b.unit,
                    tol_plus=dim_b.tol_plus,
                    tol_minus=dim_b.tol_minus,
                    type=dim_b.type,
                    source=dim_b.source,
                    confidence=dim_b.confidence * 0.7,
                    bbox=dim_b.bbox,
                    view=dim_b.view,
                    status=DimensionStatus.NEEDS_HUMAN,  # Single pass only -> must have human confirmation
                    evidence=evidence,
                    notes=f"Detected only in Pass B | {dim_b.notes or ''}".strip(),
                )
            )

    return reconciled


def merge_features(
    pass_a_features: List[FeatureSpec],
    pass_b_features: List[FeatureSpec],
) -> List[FeatureSpec]:
    """
    Merge CAD features identified across passes.
    Consolidates parameters and merges dimension references.
    """
    features: List[FeatureSpec] = []
    seen_ids = set()

    # Pass A features
    for f_a in pass_a_features:
        seen_ids.add(f_a.id)
        # Find matching in Pass B to enrich parameters
        f_b = next((fb for fb in pass_b_features if fb.id == f_a.id or fb.type == f_a.type), None)
        merged_params = dict(f_a.parameters)
        merged_dims = list(f_a.dimension_ids)

        if f_b:
            for k, v in f_b.parameters.items():
                if k not in merged_params:
                    merged_params[k] = v
            for did in f_b.dimension_ids:
                if did not in merged_dims:
                    merged_dims.append(did)

        features.append(
            FeatureSpec(
                id=f_a.id,
                type=f_a.type,
                dimension_ids=merged_dims,
                parameters=merged_params,
                parent_feature_id=f_a.parent_feature_id or (f_b.parent_feature_id if f_b else None),
            )
        )

    # Any unique features from Pass B
    for f_b in pass_b_features:
        if f_b.id not in seen_ids and not any(f.type == f_b.type and f.parameters == f_b.parameters for f in features):
            features.append(f_b)

    return features


def reconcile_drawing_specs(
    pass_a: DrawingSpec,
    pass_b: DrawingSpec,
    ocr_matches: Dict[str, Optional[float]],
    ocr_raw_text: Optional[Dict[str, str]] = None,
    tolerance: float = DEFAULT_COMPARISON_TOLERANCE,
) -> DrawingSpec:
    """
    Master reconciliation pipeline:
    1. Reconcile dimensions (Pass A + Pass B + OCR)
    2. Merge CAD features
    3. Merge title block & general notes
    4. Run engineering sanity checks
    5. Aggregate ambiguities
    """
    reconciled_dims = reconcile_dimensions(
        pass_a_dims=pass_a.dimensions,
        pass_b_dims=pass_b.dimensions,
        ocr_matches=ocr_matches,
        ocr_raw_text=ocr_raw_text,
        tolerance=tolerance,
    )

    reconciled_features = merge_features(pass_a.features, pass_b.features)

    # Combine unique notes and ambiguities
    all_notes = list(dict.fromkeys(pass_a.notes + pass_b.notes))
    all_ambiguities = list(dict.fromkeys(pass_a.ambiguities + pass_b.ambiguities))

    # Add flags for unverified dimensions to ambiguities
    for d in reconciled_dims:
        if d.status == DimensionStatus.NEEDS_HUMAN:
            all_ambiguities.append(
                f"Dimension '{d.name}' ({d.id}) requires human review: {d.notes or 'Verification incomplete'}"
            )

    spec = DrawingSpec(
        drawing_number=pass_a.drawing_number or pass_b.drawing_number,
        title=pass_a.title or pass_b.title,
        revision=pass_a.revision or pass_b.revision,
        unit=pass_a.unit or pass_b.unit or "mm",
        material=pass_a.material or pass_b.material,
        general_tolerance=pass_a.general_tolerance or pass_b.general_tolerance or "ISO 2768-m",
        dimensions=reconciled_dims,
        features=reconciled_features,
        notes=all_notes,
        ambiguities=all_ambiguities,
    )

    # Run engineering sanity rules check
    sanity_results = run_all_sanity_checks(spec)
    spec.sanity_checks = sanity_results

    # Flag any sanity check failures
    for sr in sanity_results:
        if not sr.passed and sr.severity == "ERROR":
            spec.ambiguities.append(f"Sanity Rule Failure [{sr.rule_id}]: {sr.message}")

    logger.info(
        f"Reconciliation completed: {len(spec.dimensions)} dims "
        f"({sum(1 for d in spec.dimensions if d.is_verified)} auto-verified, "
        f"{len(spec.pending_human_dimensions)} pending human), "
        f"{len(spec.sanity_checks)} sanity checks evaluated"
    )

    return spec
