"use client";

import React from "react";
import { DimensionSpec } from "@/types/spec";
import { ShieldCheck, ShieldAlert, CheckCircle2, AlertCircle } from "lucide-react";

interface ReviewProgressProps {
  dimensions: DimensionSpec[];
  onGenerateClick?: () => void;
  isGenerating?: boolean;
  className?: string;
}

export function ReviewProgress({
  dimensions,
  onGenerateClick,
  isGenerating = false,
  className = "",
}: ReviewProgressProps) {
  const total = dimensions.length;
  const verified = dimensions.filter(
    (d) =>
      (d.status === "verified_auto" ||
        d.status === "human_confirmed" ||
        d.status === "human_entered") &&
      d.value !== null &&
      d.value !== undefined
  ).length;

  const autoVerified = dimensions.filter((d) => d.status === "verified_auto" && d.value !== null).length;
  const humanConfirmed = dimensions.filter(
    (d) => (d.status === "human_confirmed" || d.status === "human_entered") && d.value !== null
  ).length;
  const needsHuman = total - verified;

  const isAllVerified = total > 0 && verified === total;
  const percentage = total > 0 ? Math.round((verified / total) * 100) : 0;

  return (
    <div className={`flex items-center gap-6 ${className}`}>
      {/* Detailed Status Breakdown */}
      <div className="hidden lg:flex items-center gap-3 text-xs font-mono">
        <span className="flex items-center gap-1.5 text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          {autoVerified} Auto
        </span>
        <span className="flex items-center gap-1.5 text-cyan-400">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          {humanConfirmed} Confirmed
        </span>
        {needsHuman > 0 && (
          <span className="flex items-center gap-1.5 text-amber-400 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            {needsHuman} Attention Needed
          </span>
        )}
      </div>

      {/* Progress Bar & Metric */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-xs font-mono font-bold text-white">
            {verified} of {total} verified
          </div>
          <div className="text-[10px] font-mono text-slate-400">
            {percentage}% complete
          </div>
        </div>

        <div className="w-32 h-2.5 rounded-full bg-slate-800 border border-slate-700/60 overflow-hidden relative">
          <div
            className={`h-full transition-all duration-300 ${
              isAllVerified ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.6)]" : "bg-amber-400"
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Gated Action Button */}
      <button
        disabled={!isAllVerified || isGenerating}
        onClick={onGenerateClick}
        className={`px-4 py-2 rounded-md text-xs font-mono font-semibold tracking-wider uppercase transition-all flex items-center gap-2 select-none ${
          isAllVerified
            ? "bg-cyan-500 hover:bg-cyan-400 text-slate-950 cursor-pointer shadow-lg shadow-cyan-950 ring-1 ring-cyan-300"
            : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700/80"
        }`}
      >
        {isAllVerified ? (
          <>
            <ShieldCheck className="w-4 h-4 text-slate-950" />
            {isGenerating ? "Synthesizing CAD..." : "Generate 3D Solid Model"}
          </>
        ) : (
          <>
            <ShieldAlert className="w-4 h-4 text-amber-500" />
            Verification Required ({needsHuman})
          </>
        )}
      </button>
    </div>
  );
}
