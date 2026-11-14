import React from "react";
import { ReviewWorkspace } from "@/components/ReviewWorkspace";
import { DimensionSpec } from "@/types/spec";

// Initial demonstration dimensions matching precision flange drawing
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
    bbox: { x_min: 0.15, y_min: 0.8, x_max: 0.85, y_max: 0.88 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 120.0,
      claude_pass_b: 120.0,
      ocr_reading: 120.0,
      agreement_score: 1.0,
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
    bbox: { x_min: 0.88, y_min: 0.2, x_max: 0.95, y_max: 0.75 },
    view: "front",
    status: "verified_auto",
    evidence: {
      claude_pass_a: 80.0,
      claude_pass_b: 80.0,
      ocr_reading: 80.0,
      agreement_score: 1.0,
    },
  },
  {
    id: "dim_03",
    name: "Center Bore Diameter",
    value: 40.0,
    unit: "mm",
    tol_plus: 0.02,
    tol_minus: 0.0,
    type: "diameter",
    source: "printed",
    confidence: 0.7,
    bbox: { x_min: 0.45, y_min: 0.45, x_max: 0.55, y_max: 0.55 },
    view: "front",
    status: "needs_human",  // Discrepancy between Claude B and OCR
    evidence: {
      claude_pass_a: 40.0,
      claude_pass_b: 40.0,
      ocr_reading: 40.5,
      agreement_score: 0.66,
      raw_ocr_text: "Ø40.5?",
    },
  },
  {
    id: "dim_04",
    name: "Plate Thickness",
    value: null,  // Missing from drawing
    unit: "mm",
    tol_plus: 0.05,
    tol_minus: 0.05,
    type: "linear",
    source: "missing",
    confidence: 0.0,
    bbox: { x_min: 0.05, y_min: 0.4, x_max: 0.12, y_max: 0.6 },
    view: "side",
    status: "needs_human",  // Requires human entry
    evidence: {
      claude_pass_a: null,
      claude_pass_b: null,
      ocr_reading: null,
      agreement_score: 0.0,
    },
    notes: "Thickness not specified in front projection",
  },
];

export default async function JobReviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ReviewWorkspace jobId={id} initialDimensions={sampleDimensions} />;
}
