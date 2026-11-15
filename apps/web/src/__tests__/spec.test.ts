import { describe, it, expect } from "vitest";
import { DimensionSpec, DrawingSpec, DimensionStatus } from "../types/spec";

describe("Prime CAD Gating Logic", () => {
  const mockDimensions: DimensionSpec[] = [
    {
      id: "dim-1",
      name: "Outer Diameter",
      value: 90.0,
      tol_plus: 0.1,
      tol_minus: -0.1,
      unit: "mm",
      type: "diameter",
      source: "printed",
      confidence: 1.0,
      view: "front",
      status: "verified_auto",
      evidence: {
        claude_pass_a: 90.0,
        claude_pass_b: 90.0,
        ocr_reading: 90.0,
        agreement_score: 1.0,
        raw_ocr_text: "Ø90±0.1",
      },
    },
    {
      id: "dim-2",
      name: "Bore Diameter",
      value: 25.0,
      tol_plus: 0.05,
      tol_minus: -0.05,
      unit: "mm",
      type: "diameter",
      source: "printed",
      confidence: 0.85,
      view: "front",
      status: "needs_human",
      evidence: {
        claude_pass_a: 25.0,
        claude_pass_b: 24.8,
        ocr_reading: 25.0,
        agreement_score: 0.85,
        raw_ocr_text: "Ø25",
      },
    },
  ];

  it("blocks CAD generation when any dimension has status needs_human", () => {
    const pendingCount = mockDimensions.filter((d) => d.status === "needs_human").length;
    const canUnblockCAD = pendingCount === 0;
    expect(canUnblockCAD).toBe(false);
  });

  it("unblocks CAD generation when all dimensions are verified_auto or human_confirmed", () => {
    const resolvedDimensions: DimensionSpec[] = mockDimensions.map((d) => ({
      ...d,
      status: d.status === "needs_human" ? "human_confirmed" : d.status,
    }));

    const pendingCount = resolvedDimensions.filter((d) => d.status === "needs_human").length;
    const canUnblockCAD = pendingCount === 0;
    expect(canUnblockCAD).toBe(true);
    expect(resolvedDimensions.every((d) => d.status === "verified_auto" || d.status === "human_confirmed")).toBe(true);
  });

  it("calculates accurate review progress percentage", () => {
    const total = mockDimensions.length;
    const verified = mockDimensions.filter((d) => d.status !== "needs_human").length;
    const progress = Math.round((verified / total) * 100);
    expect(progress).toBe(50);
  });
});

describe("Sanity Check Validation", () => {
  it("detects and flags geometry sanity violations", () => {
    const drawingSpec: DrawingSpec = {
      drawing_number: "DWG-TEST-01",
      title: "Test Specimen",
      unit: "mm",
      general_tolerance: "ISO 2768-m",
      dimensions: [
        {
          id: "d1",
          name: "OD",
          value: 30.0,
          tol_plus: 0.1,
          tol_minus: -0.1,
          unit: "mm",
          type: "diameter",
          source: "printed",
          confidence: 1.0,
          view: "front",
          status: "verified_auto",
        },
        {
          id: "d2",
          name: "Bore",
          value: 50.0,
          tol_plus: 0.05,
          tol_minus: -0.05,
          unit: "mm",
          type: "diameter",
          source: "printed",
          confidence: 1.0,
          view: "front",
          status: "verified_auto",
        },
      ],
      notes: [],
      ambiguities: [],
      sanity_checks: [
        {
          rule_id: "RULE_BORE_LE_OD",
          passed: false,
          severity: "ERROR",
          message: "Center bore diameter (50mm) exceeds outer diameter (30mm).",
          affected_dimension_ids: ["d1", "d2"],
        },
      ],
    };

    const hasFailedSanity = drawingSpec.sanity_checks.some((sc) => !sc.passed && sc.severity === "ERROR");
    expect(hasFailedSanity).toBe(true);
  });
});
