"""
Geometry validation and tolerance measurement engine using OpenCascade / CadQuery.
"""

from typing import List, Optional, Tuple
import cadquery as cq
from sketch2step_spec.drawing import DrawingSpec
from sketch2step_spec.job import GeometryMeasurement, ValidationReport


class GeometryValidator:
    """
    Validates physical solid geometry, checks OpenCascade solid topology,
    and compares measured geometry back against the confirmed drawing spec.
    """

    def validate(
        self,
        solid: cq.Workplane,
        spec: Optional[DrawingSpec] = None,
        step_roundtrip_ok: bool = True,
    ) -> ValidationReport:
        """Inspects solid model and returns comprehensive validation metrics."""
        shape = solid.val()

        # 1. Topological integrity checks
        is_valid = shape.isValid()
        # In CadQuery, a closed solid has closed shells
        is_shell_closed = True
        try:
            for s in shape.Shells():
                if not s.closed():
                    is_shell_closed = False
                    break
        except Exception:
            is_shell_closed = is_valid

        # 2. Geometric measurements
        bb = shape.BoundingBox()
        bb_x = round(bb.xlen, 4)
        bb_y = round(bb.ylen, 4)
        bb_z = round(bb.zlen, 4)
        volume = round(shape.Volume(), 4)
        area = round(shape.Area(), 4)

        face_count = len(shape.Faces())
        edge_count = len(shape.Edges())

        # Count internal cylindrical faces as holes
        hole_count = 0
        try:
            for f in shape.Faces():
                # Detect cylindrical hole faces with inward normals
                geom_type = f.geomType()
                if geom_type == "CYLINDER":
                    hole_count += 1
        except Exception:
            pass

        measurements: List[GeometryMeasurement] = []
        overall_passed = is_valid and is_shell_closed and step_roundtrip_ok

        # 3. Compare measured geometry to confirmed dimensions if spec provided
        if spec:
            measurements = self._compare_with_spec(spec, bb_x, bb_y, bb_z)
            # All measurements must pass their tolerance bands
            if not all(m.passed for m in measurements):
                overall_passed = False

        return ValidationReport(
            is_valid_solid=is_valid,
            is_shell_closed=is_shell_closed,
            has_self_intersections=not is_valid,
            bounding_box_x=bb_x,
            bounding_box_y=bb_y,
            bounding_box_z=bb_z,
            volume_mm3=volume,
            surface_area_mm2=area,
            face_count=face_count,
            edge_count=edge_count,
            hole_count=hole_count,
            step_roundtrip_ok=step_roundtrip_ok,
            measurements=measurements,
            overall_passed=overall_passed,
        )

    def _compare_with_spec(
        self, spec: DrawingSpec, bb_x: float, bb_y: float, bb_z: float
    ) -> List[GeometryMeasurement]:
        """Compares primary bounding box dimensions against linear dimensions in spec."""
        measurements: List[GeometryMeasurement] = []

        # Find candidate linear dimensions
        for dim in spec.dimensions:
            if dim.value is None:
                continue

            # Check if this dimension correlates with bb_x, bb_y, or bb_z
            measured_val = None
            dim_name_lower = dim.name.lower()

            if any(k in dim_name_lower for k in ["length", "len", "overall length"]):
                measured_val = bb_x
            elif any(k in dim_name_lower for k in ["width", "w", "overall width"]):
                measured_val = bb_y
            elif any(k in dim_name_lower for k in ["height", "h", "thickness", "thick"]):
                measured_val = bb_z

            if measured_val is not None:
                dev = round(measured_val - dim.value, 4)
                passed = (-dim.tol_minus <= dev <= dim.tol_plus) or abs(dev) < 1e-4

                source_attr = dim.status.value
                if dim.confirmed_by_user_id:
                    source_attr += f" (user: {dim.confirmed_by_user_id})"

                measurements.append(
                    GeometryMeasurement(
                        name=dim.name,
                        dimension_id=dim.id,
                        specified_value=dim.value,
                        measured_value=measured_val,
                        tolerance_plus=dim.tol_plus,
                        tolerance_minus=dim.tol_minus,
                        deviation=dev,
                        passed=passed,
                        source_attribution=source_attr,
                    )
                )

        return measurements
