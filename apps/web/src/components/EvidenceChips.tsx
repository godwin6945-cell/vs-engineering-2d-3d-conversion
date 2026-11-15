"use client";

import React from "react";
import { DimensionEvidence } from "@/types/spec";
import { Check, AlertTriangle, Layers } from "lucide-react";

interface EvidenceChipsProps {
  evidence?: DimensionEvidence | null;
  unit?: string;
  className?: string;
}

export function EvidenceChips({ evidence, unit = "mm", className = "" }: EvidenceChipsProps) {
  if (!evidence) {
    return (
      <div className={`text-[11px] text-slate-500 font-mono italic ${className}`}>
        No independent extraction evidence recorded.
      </div>
    );
  }

  const { claude_pass_a, claude_pass_b, ocr_reading, agreement_score, raw_ocr_text } = evidence;
  const isTripleMatch = agreement_score >= 0.99;
  const isTwoWayMatch = agreement_score >= 0.6;

  return (
    <div className={`p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-2.5 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-slate-600 font-mono font-bold">
          <Layers className="w-3.5 h-3.5 text-sky-700" />
          Triple Verification Evidence
        </div>
        <div className="flex items-center gap-1 text-[11px] font-mono">
          <span className="text-slate-500">Agreement:</span>
          <span
            className={`font-bold px-1.5 py-0.2 rounded ${
              isTripleMatch
                ? "bg-emerald-100 text-emerald-800"
                : isTwoWayMatch
                ? "bg-amber-100 text-amber-800"
                : "bg-red-100 text-red-800"
            }`}
          >
            {(agreement_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Reader Chips */}
      <div className="grid grid-cols-3 gap-2">
        {/* Claude Pass A */}
        <div className="p-2 rounded-md bg-white border border-slate-200 flex flex-col shadow-2xs">
          <span className="text-[10px] text-slate-500 font-mono">Claude Pass A</span>
          <span className="text-xs font-mono font-bold text-slate-900 mt-0.5">
            {claude_pass_a !== null && claude_pass_a !== undefined
              ? `${claude_pass_a} ${unit}`
              : "—"}
          </span>
        </div>

        {/* Claude Pass B */}
        <div className="p-2 rounded-md bg-white border border-slate-200 flex flex-col shadow-2xs">
          <span className="text-[10px] text-slate-500 font-mono">Claude Pass B</span>
          <span className="text-xs font-mono font-bold text-slate-900 mt-0.5">
            {claude_pass_b !== null && claude_pass_b !== undefined
              ? `${claude_pass_b} ${unit}`
              : "—"}
          </span>
        </div>

        {/* RapidOCR */}
        <div className="p-2 rounded-md bg-white border border-slate-200 flex flex-col shadow-2xs">
          <span className="text-[10px] text-slate-500 font-mono">RapidOCR</span>
          <span className="text-xs font-mono font-bold text-slate-900 mt-0.5">
            {ocr_reading !== null && ocr_reading !== undefined
              ? `${ocr_reading} ${unit}`
              : raw_ocr_text || "—"}
          </span>
        </div>
      </div>
    </div>
  );
}
