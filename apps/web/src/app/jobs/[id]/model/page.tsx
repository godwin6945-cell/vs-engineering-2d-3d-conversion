import React from "react";
import Link from "next/link";
import { ModelViewer } from "@/components/ModelViewer";
import { ValidationTable } from "@/components/ValidationTable";
import { VisualDiffPanel } from "@/components/VisualDiffPanel";
import { ValidationReport, VisualDiffResult } from "@/types/spec";
import { ArrowLeft, CheckCheck, Download, FileCheck, ShieldCheck } from "lucide-react";

// Demonstration validation report for precision flange
const sampleReport: ValidationReport = {
  is_valid_solid: true,
  is_shell_closed: true,
  has_self_intersections: false,
  bounding_box_x: 120.0,
  bounding_box_y: 80.0,
  bounding_box_z: 36.0,
  volume_mm3: 245820.4,
  surface_area_mm2: 48920.1,
  face_count: 18,
  edge_count: 42,
  hole_count: 5, // 1 center bore + 4 bolt pattern holes
  step_roundtrip_ok: true,
  overall_passed: true,
  measurements: [
    {
      name: "Overall Length",
      dimension_id: "dim_01",
      specified_value: 120.0,
      measured_value: 120.0,
      tolerance_plus: 0.1,
      tolerance_minus: 0.1,
      deviation: 0.0,
      passed: true,
      source_attribution: "verified_auto (Claude A + Pass B + RapidOCR)",
    },
    {
      name: "Overall Width",
      dimension_id: "dim_02",
      specified_value: 80.0,
      measured_value: 80.0,
      tolerance_plus: 0.1,
      tolerance_minus: 0.1,
      deviation: 0.0,
      passed: true,
      source_attribution: "verified_auto (Claude A + Pass B + RapidOCR)",
    },
    {
      name: "Center Bore Through Diameter",
      dimension_id: "dim_03",
      specified_value: 40.0,
      measured_value: 40.0,
      tolerance_plus: 0.02,
      tolerance_minus: 0.0,
      deviation: 0.0,
      passed: true,
      source_attribution: "human_confirmed by Lead Engineer",
    },
    {
      name: "Bolt Pitch Circle Diameter (PCD)",
      dimension_id: "dim_04",
      specified_value: 100.0,
      measured_value: 100.0,
      tolerance_plus: 0.05,
      tolerance_minus: 0.05,
      deviation: 0.0,
      passed: true,
      source_attribution: "verified_auto (Claude A + Pass B + RapidOCR)",
    },
    {
      name: "4x Bolt Hole Diameter",
      dimension_id: "dim_05",
      specified_value: 12.0,
      measured_value: 12.0,
      tolerance_plus: 0.1,
      tolerance_minus: 0.0,
      deviation: 0.0,
      passed: true,
      source_attribution: "verified_auto (Claude A + Pass B + RapidOCR)",
    },
  ],
};

const sampleVisualDiff: VisualDiffResult = {
  match_percentage: 98.8,
  identified_discrepancies: [
    "External rectangular perimeter matches 2D drawing within 0.02mm.",
    "Central cylindrical boss height and hole concentricity confirmed.",
    "4x bolt pattern orientation and PCD alignment verified.",
  ],
  rendered_ortho_urls: {
    front: "",
    top: "",
    side: "",
  },
};

export default async function ModelReviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="flex-1 flex flex-col bg-[#090d12] text-slate-100 font-sans min-h-[calc(100vh-3.5rem)]">
      {/* Top Header Bar */}
      <div className="h-16 border-b border-[#222f3e] bg-[#111720] px-6 flex items-center justify-between z-20 shrink-0">
        <div className="flex items-center gap-4">
          <Link
            href={`/jobs/${id}/review`}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Back to Review Workspace"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-white tracking-wide">
                3D Parametric Solid Model Review
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                STATE: VALIDATED
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono mt-0.5">
              Kernel: OpenCascade 7.7 • Modeled via Deterministic Feature Compiler
            </p>
          </div>
        </div>

        {/* Action Buttons to Sign-off / Export */}
        <div className="flex items-center gap-3">
          <Link
            href={`/jobs/${id}/export`}
            className="px-4 py-2 rounded-md bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition-all shadow-md shadow-cyan-950"
          >
            <CheckCheck className="w-4 h-4" />
            Proceed to Sign-off & Export
          </Link>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 overflow-y-auto">
        {/* Left Column: Interactive 3D WebGL Model Viewer */}
        <div className="flex flex-col space-y-4">
          <div className="h-[480px] rounded-lg border border-[#222f3e] overflow-hidden shadow-2xl relative">
            <ModelViewer />
          </div>

          {/* Visual Diff Panel */}
          <VisualDiffPanel diffResult={sampleVisualDiff} />
        </div>

        {/* Right Column: OpenCascade Geometry Validation Report */}
        <div className="flex flex-col space-y-4">
          <ValidationTable report={sampleReport} />
        </div>
      </div>
    </div>
  );
}
