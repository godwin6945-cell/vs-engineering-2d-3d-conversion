import React from "react";
import Link from "next/link";
import { AlertCircle, CheckCircle2, Clock, FileCode2, ArrowRight, Upload, HardDrive, Shield } from "lucide-react";

export default function DashboardPage() {
  // Mock demonstration data for Initial Foundations
  const reviewQueue = [
    {
      id: "job_01",
      title: "Flange Adapter Housing - Rev C",
      drawingNumber: "DWG-2026-FLG-04",
      unverifiedCount: 2,
      totalCount: 16,
      updatedAt: "10 mins ago",
      standard: "ISO 2768-m",
    },
    {
      id: "job_02",
      title: "Stepped Drive Shaft (Turned Part)",
      drawingNumber: "DWG-2026-SFT-12",
      unverifiedCount: 1,
      totalCount: 22,
      updatedAt: "25 mins ago",
      standard: "ISO 2768-f",
    },
  ];

  const recentJobs = [
    {
      id: "job_03",
      title: "L-Bracket Stiffener Mount",
      state: "EXPORTED",
      accuracyScore: "100% Confirmed",
      stepExported: true,
      time: "2 hours ago",
    },
    {
      id: "job_04",
      title: "Cylinder End Cap",
      state: "SIGNED_OFF",
      accuracyScore: "18/18 Verified",
      stepExported: false,
      time: "4 hours ago",
    },
  ];

  return (
    <div className="flex-1 p-8 max-w-7xl mx-auto w-full space-y-8">
      {/* Top Banner & Accuracy Rule Guarantee */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-lg border border-[#222f3e] bg-[#111720]/80">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />
            <h1 className="text-base font-semibold tracking-tight text-white">
              Precision CAD Pipeline Guarantee
            </h1>
          </div>
          <p className="text-xs text-slate-400 max-w-2xl">
            No dimension reaches the STEP file unless cross-checked by two vision passes and OCR, or verified by an engineer.
          </p>
        </div>

        <button className="flex items-center gap-2 px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold tracking-wide transition-colors shadow-sm self-start md:self-auto">
          <Upload className="w-3.5 h-3.5" />
          Upload New 2D Drawing
        </button>
      </div>

      {/* Hero Section: "Needs Your Review" Queue First */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
              Needs Your Review ({reviewQueue.length})
            </h2>
          </div>
          <span className="text-xs text-slate-400">
            CAD generation blocked until all pending items confirmed
          </span>
        </div>

        <div className="grid gap-3">
          {reviewQueue.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 rounded-lg border border-amber-500/30 bg-amber-950/10 hover:bg-amber-950/20 transition-all"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-semibold text-white">{item.title}</span>
                  <span className="font-mono text-xs text-slate-400 px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
                    {item.drawingNumber}
                  </span>
                  <span className="text-[11px] text-slate-400 font-mono">
                    {item.standard}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-400">
                  <span className="text-amber-400 font-medium font-mono">
                    {item.unverifiedCount} dimension{item.unverifiedCount > 1 ? "s" : ""} need verification
                  </span>
                  <span>•</span>
                  <span>{item.totalCount - item.unverifiedCount} of {item.totalCount} auto-verified</span>
                  <span>•</span>
                  <span>Updated {item.updatedAt}</span>
                </div>
              </div>

              <Link
                href={`/jobs/${item.id}/review`}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-semibold transition-colors"
              >
                Review & Confirm
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Metrics & Usage Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg border border-[#222f3e] bg-[#111720]">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-medium">Monthly Jobs</div>
          <div className="mt-2 text-2xl font-semibold font-mono text-white">42 / 500</div>
          <div className="mt-1 text-xs text-slate-500">Tier: Enterprise Business Plan</div>
        </div>

        <div className="p-4 rounded-lg border border-[#222f3e] bg-[#111720]">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-medium">Auto-Verification Rate</div>
          <div className="mt-2 text-2xl font-semibold font-mono text-cyan-400">92.4%</div>
          <div className="mt-1 text-xs text-slate-500">Claude A + Claude B + OCR</div>
        </div>

        <div className="p-4 rounded-lg border border-[#222f3e] bg-[#111720]">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-medium">Zero-False-Verified</div>
          <div className="mt-2 text-2xl font-semibold font-mono text-emerald-400">100%</div>
          <div className="mt-1 text-xs text-slate-500">Enforced by verification gate</div>
        </div>

        <div className="p-4 rounded-lg border border-[#222f3e] bg-[#111720]">
          <div className="text-xs text-slate-400 uppercase tracking-wider font-medium">CadQuery Engine</div>
          <div className="mt-2 text-2xl font-semibold font-mono text-slate-200">v2.8 (OCP)</div>
          <div className="mt-1 text-xs text-slate-500">Deterministic Feature Compiler</div>
        </div>
      </div>

      {/* Recent Completed Jobs */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
          Recent Completed Pipelines
        </h2>
        <div className="divide-y divide-[#222f3e] rounded-lg border border-[#222f3e] bg-[#111720]">
          {recentJobs.map((j) => (
            <div key={j.id} className="p-4 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <FileCode2 className="w-4 h-4 text-emerald-400" />
                <div>
                  <div className="font-semibold text-slate-200">{j.title}</div>
                  <div className="text-slate-400 font-mono text-[11px]">{j.accuracyScore}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-mono">
                  {j.state}
                </span>
                <span className="text-slate-500">{j.time}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
