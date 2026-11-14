"use client";

import React, { useState } from "react";
import { DrawingSanityCheckResult } from "@/types/spec";
import { CheckCircle2, AlertOctagon, AlertTriangle, ChevronDown, ChevronUp, Shield } from "lucide-react";

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
    <div className={`border border-[#222f3e] rounded-lg bg-[#0e141c] overflow-hidden ${className}`}>
      {/* Header Bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2.5 flex items-center justify-between bg-[#121924] hover:bg-[#161f2c] transition-colors text-left"
      >
        <div className="flex items-center gap-2">
          <Shield className={`w-4 h-4 ${hasFailures ? "text-amber-400" : "text-emerald-400"}`} />
          <span className="text-xs font-semibold text-white tracking-wide">
            Engineering Sanity Rules Engine
          </span>
          <span
            className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
              hasFailures
                ? "bg-amber-950 text-amber-300 border border-amber-800"
                : "bg-emerald-950 text-emerald-300 border border-emerald-800"
            }`}
          >
            {passedCount}/{checks.length} Passed
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>{isExpanded ? "Hide details" : "View checks"}</span>
          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </button>

      {/* Expanded Rule List */}
      {isExpanded && (
        <div className="p-3 space-y-2 border-t border-[#1c2734] divide-y divide-[#1a2330]">
          {checks.map((check) => (
            <div key={check.rule_id} className="pt-2 first:pt-0 flex items-start justify-between gap-3 text-xs">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  {check.passed ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  ) : check.severity === "ERROR" ? (
                    <AlertOctagon className="w-3.5 h-3.5 text-red-400 shrink-0" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                  )}
                  <span className="font-mono text-[11px] font-bold text-slate-200">
                    {check.rule_id}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono pl-5.5">
                  {check.message}
                </p>

                {/* Affected Dimensions Clickable Pills */}
                {check.affected_dimension_ids.length > 0 && (
                  <div className="flex items-center gap-1.5 pl-5.5 pt-1">
                    <span className="text-[10px] text-slate-500 font-mono">Affected:</span>
                    {check.affected_dimension_ids.map((id) => (
                      <button
                        key={id}
                        onClick={() => onSelectDimension && onSelectDimension(id)}
                        className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-cyan-900/60 text-cyan-300 font-mono text-[10px] border border-slate-700 transition-colors"
                      >
                        {id}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <span
                className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold uppercase shrink-0 ${
                  check.passed
                    ? "bg-emerald-950/60 text-emerald-400 border border-emerald-800/50"
                    : check.severity === "ERROR"
                    ? "bg-red-950/60 text-red-400 border border-red-800/50"
                    : "bg-amber-950/60 text-amber-400 border border-amber-800/50"
                }`}
              >
                {check.passed ? "OK" : check.severity}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
