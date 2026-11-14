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

  const currentViewUrl = diffResult.rendered_ortho_urls[selectedView];

  return (
    <div className={`bg-[#111720] border border-[#222f3e] rounded-lg p-5 font-mono space-y-4 ${className}`}>
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="text-xs font-semibold text-white tracking-wide uppercase">
              Visual Projection Comparison
            </h3>
            <span className="text-[10px] text-slate-400">
              Headless orthographic projection vs 2D drawing silhouette
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Visual Match:</span>
          <span
            className={`px-2.5 py-1 rounded text-xs font-bold ${
              diffResult.match_percentage >= 95
                ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                : "bg-amber-950 text-amber-300 border border-amber-800"
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
            className={`px-3 py-1 rounded text-xs uppercase font-bold transition-colors ${
              selectedView === view
                ? "bg-cyan-500 text-slate-950"
                : "bg-[#0b1017] text-slate-400 hover:text-white border border-[#1e293b]"
            }`}
          >
            {view} View
          </button>
        ))}
      </div>

      {/* Side-by-side or Projection View Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Rendered Orthographic View */}
        <div className="p-3 rounded bg-[#090d12] border border-[#1e293b] flex flex-col items-center justify-center aspect-[4/3] overflow-hidden">
          <span className="text-[10px] text-slate-400 uppercase mb-2">
            3D Solid Projection ({selectedView.toUpperCase()})
          </span>
          {currentViewUrl ? (
            <img
              src={currentViewUrl}
              alt={`Rendered ${selectedView} view`}
              className="max-h-full max-w-full object-contain rounded"
            />
          ) : (
            <div className="text-xs text-slate-500 italic">Projection not available</div>
          )}
        </div>

        {/* AI Difference Analysis Breakdown */}
        <div className="p-3 rounded bg-[#090d12] border border-[#1e293b] flex flex-col justify-between">
          <div>
            <span className="text-[10px] text-slate-400 uppercase">
              Differences Identified
            </span>
            <div className="mt-3 space-y-2">
              {diffResult.identified_discrepancies.map((d: string, i: number) => (
                <div key={i} className="flex items-start gap-2 text-xs">
                  {diffResult.match_percentage >= 95 ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                  )}
                  <span className="text-slate-300 leading-relaxed">{d}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-[10px] text-slate-500 pt-4 border-t border-[#1e293b] flex items-center justify-between">
            <span>Projection standard: ISO First-Angle</span>
            <span>Kernel: OpenCascade 7.7</span>
          </div>
        </div>
      </div>
    </div>
  );
}
