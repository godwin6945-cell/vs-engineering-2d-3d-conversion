"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileCode2,
  ArrowRight,
  Upload,
  HardDrive,
  Shield,
  Sparkles,
  Layers,
  Cpu,
  Check,
} from "lucide-react";

export default function DashboardPage() {
  const [demoMode, setDemoMode] = useState(true);

  // Demo parts dataset matching our synthetic benchmark suite
  const demoParts = [
    {
      id: "part_01",
      title: "Turned Flange Plate DN25",
      dwgNo: "DWG-SYN-FLG-01",
      category: "Turned & Bored",
      material: "Steel 1018",
      dimensions: 5,
      features: 3,
      status: "Ready for Review",
      unverifiedCount: 1,
      totalCount: 5,
      standard: "ISO 2768-m",
      description: "90mm OD with 4-hole PCD and 25mm center through-bore.",
    },
    {
      id: "part_07",
      title: "Milled Fixture Plate 120x80",
      dwgNo: "DWG-SYN-PLT-07",
      category: "Milled Plate",
      material: "Aluminum 6061-T6",
      dimensions: 6,
      features: 2,
      status: "Verified",
      unverifiedCount: 0,
      totalCount: 6,
      standard: "ISO 2768-m",
      description: "Base plate with precision central rectangular cavity pocket.",
    },
    {
      id: "part_13",
      title: "Turned Transmission Shaft Mod-1",
      dwgNo: "DWG-SYN-SFT-13",
      category: "Turned Shaft",
      material: "Alloy Steel 4140",
      dimensions: 4,
      features: 1,
      status: "Ready for Review",
      unverifiedCount: 1,
      totalCount: 4,
      standard: "DIN 7168-m",
      description: "Dual stepped cylindrical transmission shaft.",
    },
  ];

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
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-400 border border-cyan-800">
              ISO 10303 AP214
            </span>
          </div>
          <p className="text-xs text-slate-400 max-w-2xl">
            No dimension reaches the STEP file unless cross-checked by two vision passes and OCR, or verified by an engineer.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Demo Mode Toggle */}
          <button
            onClick={() => setDemoMode(!demoMode)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded text-xs font-medium transition-colors border ${
              demoMode
                ? "bg-cyan-950/80 text-cyan-400 border-cyan-700 hover:bg-cyan-900/60"
                : "bg-slate-900 text-slate-400 border-slate-700 hover:text-white"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            {demoMode ? "Demo Mode: Active" : "Demo Mode: Off"}
          </button>

          <button className="flex items-center gap-2 px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold tracking-wide transition-colors shadow-sm">
            <Upload className="w-3.5 h-3.5" />
            Upload 2D Drawing
          </button>
        </div>
      </div>

      {/* Demo Mode Interactive Benchmark Showcase */}
      {demoMode && (
        <div className="p-5 rounded-lg border border-cyan-500/30 bg-cyan-950/10 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-semibold text-white tracking-wide uppercase">
                Interactive Demo Benchmark Datasets (30 Synthetic Parts)
              </h2>
            </div>
            <span className="text-xs font-mono text-cyan-400">
              Ground-truth STEP & DXF pre-compiled
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Select a verified engineering specimen below to immediately inspect drawing overlays, dual-pass Claude evidence, and 3D OpenCascade geometry:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {demoParts.map((dp) => (
              <div
                key={dp.id}
                className="p-4 rounded border border-slate-800 bg-[#0d121a] hover:border-cyan-500/50 transition-all flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-cyan-400">{dp.dwgNo}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                      {dp.standard}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-white">{dp.title}</h3>
                  <p className="text-xs text-slate-400">{dp.description}</p>
                  <div className="flex items-center gap-2 text-[11px] text-slate-500">
                    <span>{dp.material}</span>
                    <span>•</span>
                    <span>{dp.dimensions} Dims</span>
                    <span>•</span>
                    <span>{dp.features} Features</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                  <span className={`text-[11px] font-mono ${dp.unverifiedCount > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                    {dp.unverifiedCount > 0 ? `${dp.unverifiedCount} needs review` : "All confirmed"}
                  </span>
                  <Link
                    href={`/jobs/${dp.id}/review`}
                    className="flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300"
                  >
                    Open Specimen
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
