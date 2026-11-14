import React from "react";
import { ReviewWorkspace } from "@/components/ReviewWorkspace";
import { DimensionSpec, DrawingSanityCheckResult } from "@/types/spec";

// Precision ISO Flange demo dataset representing real dual-pass extraction + RapidOCR cross-check output
const sampleDimensions: DimensionSpec[] = [
  {
    id: "dim_01",
    name: "Overall Length",
    value: 120.0,
    unit: "mm",
    tol_plus: 0.1,
    tol_minus: 0.1,
    type: "linear",
    source: "printed",
    confidence: 1.0,
    bbox: { x_min: 0.14, y_min: 0.86, x_max: 0.86, y_max: 0.94 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 120.0,
      claude_pass_b: 120.0,
      ocr_reading: 120.0,
      agreement_score: 1.0,
      raw_ocr_text: "120.00",
    },
  },
  {
    id: "dim_02",
    name: "Overall Width",
    value: 80.0,
    unit: "mm",
    tol_plus: 0.1,
    tol_minus: 0.1,
    type: "linear",
    source: "printed",
    confidence: 1.0,
    bbox: { x_min: 0.88, y_min: 0.16, x_max: 0.95, y_max: 0.74 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 80.0,
      claude_pass_b: 80.0,
      ocr_reading: 80.0,
      agreement_score: 1.0,
      raw_ocr_text: "80.0",
    },
  },
  {
    id: "dim_03",
    name: "Center Bore Through Diameter",
    value: 40.0,
    unit: "mm",
    tol_plus: 0.02,
    tol_minus: 0.0,
    type: "diameter",
    source: "printed",
    confidence: 0.72,
    bbox: { x_min: 0.45, y_min: 0.40, x_max: 0.55, y_max: 0.50 },
    view: "front",
    status: "needs_human", // Discrepancy between Claude (40.0) and OCR (40.5)
    evidence: {
      claude_pass_a: 40.0,
      claude_pass_b: 40.0,
      ocr_reading: 40.5,
      agreement_score: 0.67,
      raw_ocr_text: "Ø40.5?",
    },
    notes: "OCR detected 'Ø40.5?' while Pass A and Pass B read 'Ø40.0 H7'",
  },
  {
    id: "dim_04",
    name: "Bolt Pitch Circle Diameter (PCD)",
    value: 100.0,
    unit: "mm",
    tol_plus: 0.05,
    tol_minus: 0.05,
    type: "diameter",
    source: "printed",
    confidence: 1.0,
    bbox: { x_min: 0.28, y_min: 0.25, x_max: 0.72, y_max: 0.65 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 100.0,
      claude_pass_b: 100.0,
      ocr_reading: 100.0,
      agreement_score: 1.0,
      raw_ocr_text: "PCD 100",
    },
  },
  {
    id: "dim_05",
    name: "4x Bolt Hole Diameter",
    value: 12.0,
    unit: "mm",
    tol_plus: 0.1,
    tol_minus: 0.0,
    type: "diameter",
    source: "printed",
    confidence: 1.0,
    bbox: { x_min: 0.21, y_min: 0.22, x_max: 0.29, y_max: 0.32 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 12.0,
      claude_pass_b: 12.0,
      ocr_reading: 12.0,
      agreement_score: 1.0,
      raw_ocr_text: "4x Ø12",
    },
  },
  {
    id: "dim_06",
    name: "Base Flange Thickness",
    value: null, // Value missing from drawing front projection
    unit: "mm",
    tol_plus: 0.05,
    tol_minus: 0.05,
    type: "linear",
    source: "missing",
    confidence: 0.0,
    bbox: { x_min: 0.05, y_min: 0.35, x_max: 0.12, y_max: 0.55 },
    view: "side",
    status: "needs_human", // Missing value requires human input
    evidence: {
      claude_pass_a: null,
      claude_pass_b: null,
      ocr_reading: null,
      agreement_score: 0.0,
    },
    notes: "Flange thickness omitted in main projection. Engineer input required.",
  },
];

const sampleSanityChecks: DrawingSanityCheckResult[] = [
  {
    rule_id: "SANITY-001-POSITIVE-VAL",
    passed: true,
    severity: "INFO",
    message: "All physical dimension values are strictly positive.",
    affected_dimension_ids: [],
  },
  {
    rule_id: "SANITY-002-TOLERANCE-VALID",
    passed: true,
    severity: "INFO",
    message: "All tolerance specifications are valid positive bounds.",
    affected_dimension_ids: [],
  },
  {
    rule_id: "SANITY-003-UNIT-CONSISTENCY",
    passed: true,
    severity: "INFO",
    message: "All dimensions consistently specified in mm.",
    affected_dimension_ids: [],
  },
  {
    rule_id: "SANITY-005-HOLE-BOUNDARY",
    passed: true,
    severity: "INFO",
    message: "All hole placements maintain safe boundary margins.",
    affected_dimension_ids: [],
  },
  {
    rule_id: "SANITY-008-PATTERN-SPAN",
    passed: true,
    severity: "INFO",
    message: "Hole pattern layouts fit within host dimensions.",
    affected_dimension_ids: [],
  },
];

export default async function JobReviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <ReviewWorkspace
      jobId={id}
      initialDimensions={sampleDimensions}
      initialSanityChecks={sampleSanityChecks}
    />
  );
}
