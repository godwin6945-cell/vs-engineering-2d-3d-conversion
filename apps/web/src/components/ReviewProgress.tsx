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
        <span className="flex items-center gap-1.5 text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
          <span className="w-2 h-2 rounded-full bg-emerald-600" />
          {autoVerified} Auto-Verified
        </span>
        <span className="flex items-center gap-1.5 text-sky-800 bg-sky-50 px-2 py-0.5 rounded border border-sky-200">
          <span className="w-2 h-2 rounded-full bg-sky-600" />
          {humanConfirmed} Confirmed
        </span>
        {needsHuman > 0 && (
          <span className="flex items-center gap-1.5 text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
            <span className="w-2 h-2 rounded-full bg-amber-600" />
            {needsHuman} Attention Needed
          </span>
        )}
      </div>

      {/* Progress Bar & Metric */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-xs font-mono font-bold text-slate-900">
            {verified} of {total} verified
          </div>
          <div className="text-[10px] font-mono text-slate-500">
            {percentage}% complete
          </div>
        </div>

        <div className="w-32 h-2.5 rounded-full bg-slate-200 overflow-hidden relative border border-slate-300">
          <div
            className={`h-full transition-all duration-300 ${
              isAllVerified ? "bg-emerald-600" : "bg-amber-500"
            }`}
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>

      {/* Gated Action Button */}
      <button
        disabled={!isAllVerified || isGenerating}
        onClick={onGenerateClick}
        className={`px-4 py-2 rounded-md text-xs font-mono font-bold tracking-wider uppercase transition-all flex items-center gap-2 select-none ${
          isAllVerified
            ? "bg-sky-700 hover:bg-sky-800 text-white cursor-pointer shadow-sm hover:shadow"
            : "bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200"
        }`}
      >
        {isAllVerified ? (
          <>
            <ShieldCheck className="w-4 h-4 text-white" />
            {isGenerating ? "Synthesizing CAD..." : "Generate 3D Solid Model"}
          </>
        ) : (
          <>
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            Verification Required ({needsHuman})
          </>
        )}
      </button>
    </div>
  );
}
