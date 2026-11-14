// Auto-generated TypeScript definitions matching sketch2step_spec Pydantic models

export type JobState =
  | "UPLOADED"
  | "PREPROCESSED"
  | "EXTRACTED"
  | "NEEDS_REVIEW"
  | "CONFIRMED"
  | "MODELLED"
  | "VALIDATED"
  | "SIGNED_OFF"
  | "EXPORTED"
  | "FAILED";

export type OrganizationRole =
  | "OWNER"
  | "ADMIN"
  | "ENGINEER"
  | "REVIEWER"
  | "VIEWER";

export type DimensionType =
  | "linear"
  | "diameter"
  | "radius"
  | "angle"
  | "depth"
  | "thread";

export type DimensionSource = "printed" | "inferred" | "missing";

export type DimensionStatus =
  | "verified_auto"
  | "needs_human"
  | "human_confirmed"
  | "human_entered";

export type ViewType =
  | "front"
  | "top"
  | "side"
  | "isometric"
  | "detail"
  | "section"
  | "unknown";

export type FeatureType =
  | "plate"
  | "block"
  | "cylinder"
  | "stepped_shaft"
  | "flange"
  | "bracket_l"
  | "bracket_u"
  | "hole_through"
  | "hole_blind"
  | "hole_counterbore"
  | "hole_countersink"
  | "hole_pattern_linear"
  | "hole_pattern_circular"
  | "hole_pattern_grid"
  | "slot"
  | "pocket_rect"
  | "pocket_circle"
  | "pocket_obround"
  | "boss"
  | "fillet"
  | "chamfer"
  | "thread_cosmetic"
  | "thread_modelled"
  | "keyway";

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface DimensionEvidence {
  claude_pass_a?: number | null;
  claude_pass_b?: number | null;
  ocr_reading?: number | null;
  agreement_score: number;
  raw_ocr_text?: string | null;
}

export interface DimensionSpec {
  id: string;
  name: string;
  value: number | null;
  unit: string;
  tol_plus: number;
  tol_minus: number;
  type: DimensionType;
  source: DimensionSource;
  confidence: number;
  bbox?: BoundingBox | null;
  view: ViewType;
  status: DimensionStatus;
  evidence?: DimensionEvidence | null;
  notes?: string | null;
  confirmed_by_user_id?: string | null;
}

export interface FeatureSpec {
  id: string;
  type: FeatureType;
  dimension_ids: string[];
  parameters: Record<string, unknown>;
  parent_feature_id?: string | null;
}

export interface DrawingSanityCheckResult {
  rule_id: string;
  passed: bool;
  severity: "ERROR" | "WARNING";
  message: string;
  affected_dimension_ids: string[];
}

export interface DrawingSpec {
  drawing_number?: string | null;
  title?: string | null;
  revision?: string | null;
  unit: string;
  material?: string | null;
  general_tolerance: string;
  dimensions: DimensionSpec[];
  features: FeatureSpec[];
  notes: string[];
  ambiguities: string[];
  sanity_checks: DrawingSanityCheckResult[];
}

export interface GeometryMeasurement {
  name: string;
  dimension_id?: string | null;
  specified_value: number;
  measured_value: number;
  tolerance_plus: number;
  tolerance_minus: number;
  deviation: number;
  passed: boolean;
  source_attribution: string;
}

export interface ValidationReport {
  is_valid_solid: boolean;
  is_shell_closed: boolean;
  has_self_intersections: boolean;
  bounding_box_x: number;
  bounding_box_y: number;
  bounding_box_z: number;
  volume_mm3: number;
  surface_area_mm2: number;
  face_count: number;
  edge_count: number;
  hole_count: number;
  step_roundtrip_ok: boolean;
  measurements: GeometryMeasurement[];
  overall_passed: boolean;
}

export interface VisualDiffResult {
  match_percentage: number;
  identified_discrepancies: string[];
  rendered_ortho_urls: Record<string, string>;
}

export interface JobResponse {
  id: string;
  org_id: string;
  project_id?: string | null;
  title: string;
  state: JobState;
  drawing_file_url: string;
  spec?: DrawingSpec | null;
  validation_report?: ValidationReport | null;
  visual_diff?: VisualDiffResult | null;
  step_file_url?: string | null;
  cad_script_url?: string | null;
  inspection_report_pdf_url?: string | null;
  signed_off_by_user_id?: string | null;
  signed_off_at?: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  role: OrganizationRole;
  org_id: string;
  is_active: boolean;
  created_at: string;
  last_login_at?: string | null;
}

export interface OrganizationResponse {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  retention_days: number;
  allow_byok: boolean;
  created_at: string;
  updated_at: string;
}
