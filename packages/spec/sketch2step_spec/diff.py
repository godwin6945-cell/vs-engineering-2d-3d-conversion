"""
Job Versioning & Dimensional Diff Engine.
Calculates exact geometric and specification deltas between model iterations (v1 -> v2).
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from .drawing import DimensionSpec, DrawingSpec
from .job import ValidationReport


class DimensionChange(BaseModel):
    """Details of a single dimension variation across versions."""
    dimension_id: str
    name: str
    change_type: str  # "ADDED", "REMOVED", "MODIFIED", "UNCHANGED"
    old_value: Optional[float] = None
    new_value: Optional[float] = None
    value_delta: Optional[float] = None
    old_tolerance: Optional[str] = None
    new_tolerance: Optional[str] = None
    old_status: Optional[str] = None
    new_status: Optional[str] = None


class GeometryDiff(BaseModel):
    """Calculated OpenCascade physical delta across 3D model versions."""
    volume_delta_mm3: float = 0.0
    surface_area_delta_mm2: float = 0.0
    bounding_box_delta_x: float = 0.0
    bounding_box_delta_y: float = 0.0
    bounding_box_delta_z: float = 0.0
    face_count_delta: int = 0
    edge_count_delta: int = 0


class JobVersionDiff(BaseModel):
    """Complete version delta report."""
    base_job_id: str
    base_version: int
    target_job_id: str
    target_version: int
    dimension_changes: List[DimensionChange] = Field(default_factory=list)
    geometry_diff: Optional[GeometryDiff] = None
    summary: str = ""


def compute_spec_diff(
    spec_old: DrawingSpec,
    spec_new: DrawingSpec,
) -> List[DimensionChange]:
    """Computes dimensional differences between two DrawingSpec versions."""
    changes: List[DimensionChange] = []
    old_dims: Dict[str, DimensionSpec] = {d.id: d for d in spec_old.dimensions}
    new_dims: Dict[str, DimensionSpec] = {d.id: d for d in spec_new.dimensions}

    all_ids = list(dict.fromkeys(list(old_dims.keys()) + list(new_dims.keys())))

    for dim_id in all_ids:
        d_old = old_dims.get(dim_id)
        d_new = new_dims.get(dim_id)

        if d_old is None and d_new is not None:
            changes.append(
                DimensionChange(
                    dimension_id=dim_id,
                    name=d_new.name,
                    change_type="ADDED",
                    new_value=d_new.value,
                    new_tolerance=f"+{d_new.tol_plus}/-{d_new.tol_minus}",
                    new_status=d_new.status.value,
                )
            )
        elif d_old is not None and d_new is None:
            changes.append(
                DimensionChange(
                    dimension_id=dim_id,
                    name=d_old.name,
                    change_type="REMOVED",
                    old_value=d_old.value,
                    old_tolerance=f"+{d_old.tol_plus}/-{d_old.tol_minus}",
                    old_status=d_old.status.value,
                )
            )
        elif d_old is not None and d_new is not None:
            val_delta = None
            if d_old.value is not None and d_new.value is not None:
                val_delta = round(d_new.value - d_old.value, 4)

            is_val_changed = val_delta is not None and abs(val_delta) > 0.0001
            is_tol_changed = (d_old.tol_plus != d_new.tol_plus) or (d_old.tol_minus != d_new.tol_minus)
            is_status_changed = d_old.status != d_new.status

            if is_val_changed or is_tol_changed or is_status_changed:
                changes.append(
                    DimensionChange(
                        dimension_id=dim_id,
                        name=d_new.name,
                        change_type="MODIFIED",
                        old_value=d_old.value,
                        new_value=d_new.value,
                        value_delta=val_delta,
                        old_tolerance=f"+{d_old.tol_plus}/-{d_old.tol_minus}",
                        new_tolerance=f"+{d_new.tol_plus}/-{d_new.tol_minus}",
                        old_status=d_old.status.value,
                        new_status=d_new.status.value,
                    )
                )
            else:
                changes.append(
                    DimensionChange(
                        dimension_id=dim_id,
                        name=d_new.name,
                        change_type="UNCHANGED",
                        old_value=d_old.value,
                        new_value=d_new.value,
                        value_delta=0.0,
                        old_tolerance=f"+{d_old.tol_plus}/-{d_old.tol_minus}",
                        new_tolerance=f"+{d_new.tol_plus}/-{d_new.tol_minus}",
                        old_status=d_old.status.value,
                        new_status=d_new.status.value,
                    )
                )

    return changes


def compute_geometry_diff(
    report_old: Optional[ValidationReport],
    report_new: Optional[ValidationReport],
) -> Optional[GeometryDiff]:
    """Calculates physical B-Rep solid property differences."""
    if not report_old or not report_new:
        return None

    return GeometryDiff(
        volume_delta_mm3=round(report_new.volume_mm3 - report_old.volume_mm3, 3),
        surface_area_delta_mm2=round(report_new.surface_area_mm2 - report_old.surface_area_mm2, 3),
        bounding_box_delta_x=round(report_new.bounding_box_x - report_old.bounding_box_x, 3),
        bounding_box_delta_y=round(report_new.bounding_box_y - report_old.bounding_box_y, 3),
        bounding_box_delta_z=round(report_new.bounding_box_z - report_old.bounding_box_z, 3),
        face_count_delta=report_new.face_count - report_old.face_count,
        edge_count_delta=report_new.edge_count - report_old.edge_count,
    )
