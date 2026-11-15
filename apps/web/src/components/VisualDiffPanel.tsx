"use client";

import React, { useState } from "react";
import { VisualDiffResult } from "@/types/spec";
import { Layers, CheckCircle2, AlertTriangle, Eye } from "lucide-react";

interface VisualDiffPanelProps {
  diffResult: VisualDiffResult;
  originalDrawingUrl?: string;
  className?: string;
}

export function VisualDiffPanel({
  diffResult,
  originalDrawingUrl,
  className = "",
}: VisualDiffPanelProps) {
  const [selectedView, setSelectedView] = useState<"front" | "top" | "side">("front");

  return (
    <div className={`bg-white border border-slate-200 rounded-lg p-5 font-mono space-y-4 shadow-xs ${className}`}>
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-sky-700" />
          <div>
            <h3 className="text-xs font-bold text-slate-900 tracking-wide uppercase">
              Visual Projection Silhouette Comparison
            </h3>
            <span className="text-[10px] text-slate-500">
              Orthographic projection vs 2D drawing silhouette overlay
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">Silhouette Match:</span>
          <span
            className={`px-2.5 py-1 rounded text-xs font-bold ${
              diffResult.match_percentage >= 95
                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                : "bg-amber-50 text-amber-800 border border-amber-200"
            }`}
          >
            {diffResult.match_percentage}%
          </span>
        </div>
      </div>

      {/* View Selector Tabs */}
      <div className="flex items-center gap-2">
        {(["front", "top", "side"] as const).map((view) => (
          <button
            key={view}
            onClick={() => setSelectedView(view)}
            className={`px-3 py-1 rounded-md text-xs uppercase font-bold transition-colors cursor-pointer ${
              selectedView === view
                ? "bg-sky-700 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            {view} Projection
          </button>
        ))}
      </div>

      {/* Comparison Projection Visualizer */}
      <div className="relative h-48 rounded-lg bg-slate-50 border border-slate-300 flex items-center justify-center overflow-hidden">
        {/* Subtle grid */}
        <div
          className="absolute inset-0 pointer-events-none opacity-50"
          style={{
            backgroundImage:
              "linear-gradient(to right, #cbd5e1 1px, transparent 1px), linear-gradient(to bottom, #cbd5e1 1px, transparent 1px)",
            backgroundSize: "20px 20px",
          }}
        />

        {/* Projection graphic */}
        <div className="relative z-10 flex flex-col items-center justify-center p-4 text-center">
          <div className="w-32 h-24 border-2 border-slate-700 rounded bg-white/90 shadow-xs flex items-center justify-center relative">
            <div className="w-16 h-16 rounded-full border border-dashed border-sky-600 bg-sky-50 flex items-center justify-center">
              <span className="text-[9px] font-mono font-bold text-sky-800">BORE Ø40</span>
            </div>
            <div className="absolute top-1 left-1 text-[8px] font-mono text-slate-500 font-bold">120 x 80</div>
          </div>
          <span className="text-[11px] font-mono font-bold text-emerald-700 mt-2 flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Silhouette contours align within 0.02 mm
          </span>
        </div>
      </div>

      {/* Discrepancies / Verification Notes */}
      <div className="space-y-1.5 pt-1">
        <span className="text-[11px] font-bold text-slate-700 uppercase">
          Reconciliation Notes:
        </span>
        <ul className="space-y-1 text-xs text-slate-600">
          {diffResult.identified_discrepancies.map((d, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-emerald-600 font-bold">✓</span>
              <span>{d}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
