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
    <div className={`p-3 rounded bg-[#0b1017] border border-[#222f3e] space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-slate-400 font-mono">
          <Layers className="w-3 h-3 text-cyan-400" />
          Independent Readers Cross-Check
        </div>
        <div className="flex items-center gap-1 text-[11px] font-mono">
          <span className="text-slate-400">Score:</span>
          <span
            className={`font-bold ${
              isTripleMatch
                ? "text-emerald-400"
                : isTwoWayMatch
                ? "text-amber-400"
                : "text-red-400"
            }`}
          >
            {(agreement_score * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Reader Chips */}
      <div className="grid grid-cols-3 gap-2">
        {/* Claude Pass A */}
        <div className="p-2 rounded bg-slate-900 border border-slate-800 flex flex-col">
          <span className="text-[10px] text-slate-400 font-mono">Claude Pass A</span>
          <span className="text-xs font-mono font-bold text-slate-100 mt-0.5">
            {claude_pass_a !== null && claude_pass_a !== undefined
              ? `${claude_pass_a} ${unit}`
              : "—"}
          </span>
        </div>

        {/* Claude Pass B */}
        <div className="p-2 rounded bg-slate-900 border border-slate-800 flex flex-col">
          <span className="text-[10px] text-slate-400 font-mono">Claude Pass B</span>
          <span className="text-xs font-mono font-bold text-slate-100 mt-0.5">
            {claude_pass_b !== null && claude_pass_b !== undefined
              ? `${claude_pass_b} ${unit}`
              : "—"}
          </span>
        </div>

        {/* RapidOCR */}
        <div className="p-2 rounded bg-slate-900 border border-slate-800 flex flex-col">
          <div className="flex items-center justify-between">
            <span className="text-[10px] text-slate-400 font-mono">RapidOCR</span>
            {raw_ocr_text && (
              <span className="text-[9px] text-slate-500 font-mono truncate max-w-[50px]" title={raw_ocr_text}>
                {raw_ocr_text}
              </span>
            )}
          </div>
          <span className="text-xs font-mono font-bold text-slate-100 mt-0.5">
            {ocr_reading !== null && ocr_reading !== undefined
              ? `${ocr_reading} ${unit}`
              : "—"}
          </span>
        </div>
      </div>

      {/* Verification Explanation */}
      <div className="text-[11px] font-mono flex items-center gap-1.5 pt-0.5">
        {isTripleMatch ? (
          <>
            <Check className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-emerald-300">
              Pass A, Pass B, and OCR reading agree exactly.
            </span>
          </>
        ) : (
          <>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-amber-300">
              Discrepancy detected across readers. Human confirmation required.
            </span>
          </>
        )}
      </div>
    </div>
  );
}
