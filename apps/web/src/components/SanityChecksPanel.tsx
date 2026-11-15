"use client";

import React, { useState } from "react";
import { DrawingSanityCheckResult } from "@/types/spec";
import { CheckCircle2, AlertOctagon, AlertTriangle, ChevronDown, ChevronUp, ShieldCheck } from "lucide-react";

interface SanityChecksPanelProps {
  checks: DrawingSanityCheckResult[];
  onSelectDimension?: (id: string) => void;
  className?: string;
}

export function SanityChecksPanel({
  checks,
  onSelectDimension,
  className = "",
}: SanityChecksPanelProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const passedCount = checks.filter((c) => c.passed).length;
  const failureCount = checks.filter((c) => !c.passed).length;
  const hasFailures = failureCount > 0;

  if (checks.length === 0) return null;

  return (
    <div className={`border border-slate-200 rounded-lg bg-white overflow-hidden shadow-2xs ${className}`}>
      {/* Header Bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2.5 flex items-center justify-between bg-slate-50 hover:bg-slate-100 transition-colors text-left cursor-pointer"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className={`w-4 h-4 ${hasFailures ? "text-amber-600" : "text-emerald-600"}`} />
          <span className="text-xs font-bold text-slate-900 tracking-wide">
            Engineering Sanity Checks (8 Rules)
          </span>
          <span
            className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
              hasFailures
                ? "bg-amber-100 text-amber-800 border border-amber-200"
                : "bg-emerald-100 text-emerald-800 border border-emerald-200"
            }`}
          >
            {passedCount}/{checks.length} Passed
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-500 font-medium">
          <span>{isExpanded ? "Hide rules" : "View rules"}</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded Rule List */}
      {isExpanded && (
        <div className="p-3 space-y-2 border-t border-slate-200 divide-y divide-slate-100">
          {checks.map((check) => (
            <div key={check.rule_id} className="pt-2 first:pt-0 flex items-start justify-between gap-3 text-xs">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] text-slate-500 font-bold">{check.rule_id}</span>
                  <span className="font-semibold text-slate-900">{check.message}</span>
                </div>
                {check.affected_dimension_ids.length > 0 && (
                  <div className="flex items-center gap-1 text-[10px] font-mono text-slate-500">
                    <span>Targeted:</span>
                    {check.affected_dimension_ids.map((id) => (
                      <button
                        key={id}
                        onClick={() => onSelectDimension?.(id)}
                        className="px-1.5 py-0.5 rounded bg-slate-100 text-sky-700 hover:underline font-bold"
                      >
                        {id}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <span
                className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                  check.passed
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    : "bg-red-50 text-red-800 border border-red-200"
                }`}
              >
                {check.passed ? "PASS" : "FAIL"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
