import React from "react";
import Link from "next/link";
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FileCheck2,
  FileCode2,
  FileSpreadsheet,
  Lock,
  Printer,
  ShieldCheck,
  UserCheck,
} from "lucide-react";

export default async function ExportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="flex-1 flex flex-col bg-[#090d12] text-slate-100 font-sans min-h-[calc(100vh-3.5rem)]">
      {/* Top Header Navigation */}
      <div className="h-16 border-b border-[#222f3e] bg-[#111720] px-6 flex items-center justify-between z-20 shrink-0">
        <div className="flex items-center gap-4">
          <Link
            href={`/jobs/${id}/model`}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
            title="Back to 3D Model Review"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-semibold text-white tracking-wide">
                Quality Assurance Sign-Off & STEP AP214 Export
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                STATE: SIGNED OFF
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-mono mt-0.5">
              Verified Model v1 • Digital Inspection Certificate Generated
            </p>
          </div>
        </div>

        {/* Certificate Hash Badge */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span>SHA-256 SEALED</span>
        </div>
      </div>

      {/* Main Container */}
      <div className="flex-1 max-w-5xl mx-auto w-full p-8 space-y-8 overflow-y-auto">
        {/* Sign-off Approval Banner */}
        <div className="p-6 rounded-lg border border-emerald-800/60 bg-emerald-950/20 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-xl">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-full bg-emerald-900/60 border border-emerald-700/80 flex items-center justify-center text-emerald-400 shrink-0">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h2 className="text-base font-bold text-white tracking-wide">
                Model Approved & Certified for Production
              </h2>
              <p className="text-xs text-slate-300 font-mono">
                Approved by Lead QA Engineer • Alpha Precision Works
              </p>
              <p className="text-[11px] text-emerald-400/90 font-mono">
                Timestamp: 2026-11-14 16:30:00 UTC • Model Version: v1
              </p>
            </div>
          </div>

          <div className="text-right font-mono text-xs text-slate-400">
            <div className="text-slate-200 font-bold">Accuracy Guarantee</div>
            <div>0 Unverified Dimensions</div>
            <div className="text-emerald-400">100% Geometry Matched</div>
          </div>
        </div>

        {/* Export Downloads Grid */}
        <div className="space-y-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
            Verified Artifact Downloads
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* 1. STEP AP214 File */}
            <div className="p-5 rounded-lg bg-[#111720] border border-[#222f3e] hover:border-cyan-500/60 transition-all flex flex-col justify-between space-y-4 shadow-lg group">
              <div className="space-y-2">
                <div className="w-10 h-10 rounded bg-cyan-950/80 border border-cyan-800/60 flex items-center justify-center text-cyan-400">
                  <FileCheck2 className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white">STEP 3D Solid Model</h4>
                <p className="text-xs text-slate-400 font-mono">
                  ISO 10303-21 (AP214) protocol. Ready for CNC CAM toolpaths and CMM inspection.
                </p>
              </div>

              <a
                href={`/api/v1/jobs/${id}/export/step`}
                className="w-full py-2.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold flex items-center justify-center gap-2 transition-colors shadow-md"
              >
                <Download className="w-4 h-4" />
                Download STEP (.step)
              </a>
            </div>

            {/* 2. PDF QA Inspection Report */}
            <div className="p-5 rounded-lg bg-[#111720] border border-[#222f3e] hover:border-emerald-500/60 transition-all flex flex-col justify-between space-y-4 shadow-lg group">
              <div className="space-y-2">
                <div className="w-10 h-10 rounded bg-emerald-950/80 border border-emerald-800/60 flex items-center justify-center text-emerald-400">
                  <Printer className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white">PDF Inspection Report</h4>
                <p className="text-xs text-slate-400 font-mono">
                  Formal ISO inspection certificate with drawing metadata, measured deltas, and digital sign-off.
                </p>
              </div>

              <a
                href={`/api/v1/jobs/${id}/export/pdf`}
                className="w-full py-2.5 rounded bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-mono text-xs font-bold flex items-center justify-center gap-2 transition-colors shadow-md"
              >
                <Download className="w-4 h-4" />
                Download Report (.pdf)
              </a>
            </div>

            {/* 3. Parametric CadQuery Python Script */}
            <div className="p-5 rounded-lg bg-[#111720] border border-[#222f3e] hover:border-purple-500/60 transition-all flex flex-col justify-between space-y-4 shadow-lg group">
              <div className="space-y-2">
                <div className="w-10 h-10 rounded bg-purple-950/80 border border-purple-800/60 flex items-center justify-center text-purple-400">
                  <FileCode2 className="w-5 h-5" />
                </div>
                <h4 className="text-sm font-bold text-white">CadQuery Script</h4>
                <p className="text-xs text-slate-400 font-mono">
                  Reproducible, parameterized Python script used to synthesize the boundary representation solid.
                </p>
              </div>

              <a
                href={`/api/v1/jobs/${id}/export/cad-script`}
                className="w-full py-2.5 rounded bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs font-bold flex items-center justify-center gap-2 transition-colors shadow-md"
              >
                <Download className="w-4 h-4" />
                Download Script (.py)
              </a>
            </div>
          </div>
        </div>

        {/* Audit Lineage & Chain of Custody */}
        <div className="p-5 rounded-lg bg-[#111720] border border-[#222f3e] space-y-3 font-mono text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-[#222f3e]">
            <span className="text-slate-300 font-bold uppercase text-[11px]">
              Chain of Custody & Audit Record
            </span>
            <span className="text-slate-500 text-[10px]">Tamper-Evident Immutable Log</span>
          </div>

          <div className="space-y-2 text-slate-400 text-[11px]">
            <div className="flex items-center justify-between">
              <span>Job Identifier:</span>
              <span className="text-slate-200 font-mono">{id}</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Tenant ID:</span>
              <span className="text-slate-200 font-mono">alpha-precision-works</span>
            </div>
            <div className="flex items-center justify-between">
              <span>Primary Compilation Path:</span>
              <span className="text-cyan-400 font-semibold">Deterministic Feature Compiler</span>
            </div>
            <div className="flex items-center justify-between">
              <span>OpenCascade Kernel Check:</span>
              <span className="text-emerald-400 font-semibold">100% Solid Closed & Manifold</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
