"use client";

import React, { useState, useEffect } from "react";
import { DimensionSpec, DimensionStatus } from "@/types/spec";
import { Check, AlertTriangle, Eye, ShieldCheck, ChevronRight, Edit3 } from "lucide-react";

interface ReviewWorkspaceProps {
  jobId: string;
  initialDimensions: DimensionSpec[];
}

export function ReviewWorkspace({ jobId, initialDimensions }: ReviewWorkspaceProps) {
  const [dimensions, setDimensions] = useState<DimensionSpec[]>(initialDimensions);
  const [selectedDimId, setSelectedDimId] = useState<string | null>(initialDimensions[0]?.id || null);
  const [editingValue, setEditingValue] = useState<string>("");

  const verifiedCount = dimensions.filter(
    (d) =>
      (d.status === "verified_auto" ||
        d.status === "human_confirmed" ||
        d.status === "human_entered") &&
      d.value !== null
  ).length;

  const totalCount = dimensions.length;
  const isAllVerified = verifiedCount === totalCount;

  const selectedDim = dimensions.find((d) => d.id === selectedDimId);

  // Sync edit input when selected dimension changes
  useEffect(() => {
    if (selectedDim) {
      setEditingValue(selectedDim.value !== null ? String(selectedDim.value) : "");
    }
  }, [selectedDimId, selectedDim]);

  // Keyboard navigation: J/K to move, Enter to confirm, E to edit
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        if (e.key === "Enter") {
          e.preventDefault();
          handleConfirmCurrent();
        }
        return;
      }

      const currentIndex = dimensions.findIndex((d) => d.id === selectedDimId);
      if (e.key === "j" || e.key === "ArrowDown") {
        e.preventDefault();
        const nextIndex = (currentIndex + 1) % dimensions.length;
        setSelectedDimId(dimensions[nextIndex].id);
      } else if (e.key === "k" || e.key === "ArrowUp") {
        e.preventDefault();
        const prevIndex = (currentIndex - 1 + dimensions.length) % dimensions.length;
        setSelectedDimId(dimensions[prevIndex].id);
      } else if (e.key === "e") {
        e.preventDefault();
        const input = document.getElementById("dimension-input");
        input?.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [dimensions, selectedDimId, editingValue]);

  const handleConfirmCurrent = () => {
    if (!selectedDimId) return;
    const num = parseFloat(editingValue);
    if (isNaN(num)) return;

    setDimensions((prev) =>
      prev.map((d) => {
        if (d.id === selectedDimId) {
          return {
            ...d,
            value: num,
            status: "human_confirmed" as DimensionStatus,
          };
        }
        return d;
      })
    );

    // Auto advance to next dimension needing attention
    const currentIndex = dimensions.findIndex((d) => d.id === selectedDimId);
    const nextDim = dimensions.find(
      (d, i) => i > currentIndex && d.status === "needs_human"
    ) || dimensions.find((d) => d.status === "needs_human");

    if (nextDim) {
      setSelectedDimId(nextDim.id);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-[#090d12]">
      {/* Top Review Bar & Progress */}
      <div className="h-14 border-b border-[#222f3e] bg-[#111720] px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-sm font-semibold text-white tracking-wide">
              Engineering Drawing Review Workspace
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              Shortcuts: <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">J</kbd>/<kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">K</kbd> navigate, <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">Enter</kbd> confirm, <kbd className="px-1 py-0.5 bg-slate-800 rounded text-slate-300">E</kbd> edit
            </p>
          </div>
        </div>

        {/* Verification Progress and Gated Action Button */}
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <span className="text-xs font-mono font-medium text-slate-300">
              {verifiedCount} of {totalCount} verified
            </span>
            <div className="w-36 h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  isAllVerified ? "bg-emerald-400" : "bg-amber-400"
                }`}
                style={{ width: `${(verifiedCount / totalCount) * 100}%` }}
              />
            </div>
          </div>

          <button
            disabled={!isAllVerified}
            className={`px-4 py-2 rounded text-xs font-semibold tracking-wider uppercase transition-all flex items-center gap-2 ${
              isAllVerified
                ? "bg-cyan-500 hover:bg-cyan-400 text-slate-950 cursor-pointer shadow-lg shadow-cyan-950"
                : "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            {isAllVerified ? "Generate 3D Solid Model" : "Verification Required"}
          </button>
        </div>
      </div>

      {/* Split Workspace View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: 2D Drawing Interactive Canvas View */}
        <div className="flex-1 relative bg-[#0b1017] border-r border-[#222f3e] flex items-center justify-center p-6 select-none overflow-hidden">
          <div className="relative w-full max-w-2xl aspect-[4/3] bg-slate-900/60 border border-slate-800 rounded-lg flex items-center justify-center shadow-2xl">
            {/* Drawing Schematic Background Wireframe */}
            <svg className="w-full h-full p-8" viewBox="0 0 400 300">
              {/* Part Silhouette */}
              <rect
                x="60"
                y="60"
                width="280"
                height="180"
                rx="8"
                fill="none"
                stroke="#334155"
                strokeWidth="2"
              />
              <circle cx="200" cy="150" r="40" fill="none" stroke="#334155" strokeWidth="2" strokeDasharray="4 4" />
              <circle cx="100" cy="100" r="10" fill="none" stroke="#334155" strokeWidth="1.5" />
              <circle cx="300" cy="100" r="10" fill="none" stroke="#334155" strokeWidth="1.5" />
              <circle cx="100" cy="200" r="10" fill="none" stroke="#334155" strokeWidth="1.5" />
              <circle cx="300" cy="200" r="10" fill="none" stroke="#334155" strokeWidth="1.5" />

              {/* Centerlines */}
              <line x1="40" y1="150" x2="360" y2="150" stroke="#1e293b" strokeDasharray="6 3" />
              <line x1="200" y1="40" x2="200" y2="260" stroke="#1e293b" strokeDasharray="6 3" />
            </svg>

            {/* Interactive Dimension Bounding Box Overlays */}
            {dimensions.map((dim) => {
              if (!dim.bbox) return null;
              const isSelected = dim.id === selectedDimId;
              const isVerified =
                dim.status === "verified_auto" ||
                dim.status === "human_confirmed" ||
                dim.status === "human_entered";

              return (
                <div
                  key={dim.id}
                  onClick={() => setSelectedDimId(dim.id)}
                  style={{
                    left: `${dim.bbox.x_min * 100}%`,
                    top: `${dim.bbox.y_min * 100}%`,
                    width: `${(dim.bbox.x_max - dim.bbox.x_min) * 100}%`,
                    height: `${(dim.bbox.y_max - dim.bbox.y_min) * 100}%`,
                  }}
                  className={`absolute cursor-pointer border transition-all flex items-center justify-center ${
                    isSelected
                      ? "border-cyan-400 bg-cyan-500/20 shadow-[0_0_12px_rgba(6,182,212,0.4)] z-20"
                      : isVerified
                      ? "border-emerald-500/60 bg-emerald-500/10 hover:border-emerald-400 z-10"
                      : "border-amber-400/80 bg-amber-500/20 hover:border-amber-400 z-10 animate-pulse"
                  }`}
                >
                  <span
                    className={`text-[10px] font-mono px-1 rounded font-bold ${
                      isSelected
                        ? "bg-cyan-500 text-slate-950"
                        : isVerified
                        ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                        : "bg-amber-950 text-amber-300 border border-amber-800"
                    }`}
                  >
                    {dim.value !== null ? `${dim.value}` : "???"}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="absolute bottom-4 left-6 text-xs text-slate-500 font-mono">
            Interactive Drawing Canvas • Click any box or table row to inspect
          </div>
        </div>

        {/* Right: Dimension Extraction Table & Verification Controls */}
        <div className="w-[460px] flex flex-col bg-[#111720] border-l border-[#222f3e]">
          {/* Selected Dimension Detail Card */}
          {selectedDim && (
            <div className="p-4 border-b border-[#222f3e] bg-[#141d28] space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-mono tracking-wider text-slate-400">
                    Selected Dimension ({selectedDim.id})
                  </span>
                  <div className="text-sm font-semibold text-white">{selectedDim.name}</div>
                </div>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded font-medium ${
                    selectedDim.status === "verified_auto"
                      ? "bg-emerald-950 text-emerald-400 border border-emerald-800"
                      : selectedDim.status === "human_confirmed"
                      ? "bg-cyan-950 text-cyan-400 border border-cyan-800"
                      : "bg-amber-950 text-amber-400 border border-amber-800"
                  }`}
                >
                  {selectedDim.status.replace("_", " ").toUpperCase()}
                </span>
              </div>

              {/* Evidence Chips: Claude A, Claude B, OCR */}
              {selectedDim.evidence && (
                <div className="p-2.5 rounded bg-[#0b1017] border border-[#222f3e] space-y-1.5">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">
                    Independent Reader Evidence
                  </div>
                  <div className="flex items-center gap-2 text-xs font-mono">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Claude A: {selectedDim.evidence.claude_pass_a ?? "—"}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Claude B: {selectedDim.evidence.claude_pass_b ?? "—"}
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      OCR: {selectedDim.evidence.ocr_reading ?? "—"}
                    </span>
                  </div>
                </div>
              )}

              {/* Human Input / Confirmation Field */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-slate-300">
                  {selectedDim.value === null
                    ? "Value not detected on drawing. Enter value (mm):"
                    : "Confirm or edit nominal value (mm):"}
                </label>
                <div className="flex gap-2">
                  <input
                    id="dimension-input"
                    type="number"
                    step="0.01"
                    value={editingValue}
                    onChange={(e) => setEditingValue(e.target.value)}
                    placeholder="Enter mm"
                    className="flex-1 px-3 py-1.5 rounded bg-[#090d12] border border-[#222f3e] text-sm font-mono text-white focus:outline-none focus:border-cyan-500"
                  />
                  <button
                    onClick={handleConfirmCurrent}
                    className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  >
                    <Check className="w-3.5 h-3.5" />
                    Confirm
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Grouped Dimension Table */}
          <div className="flex-1 overflow-y-auto divide-y divide-[#1e293b]">
            {dimensions.map((dim) => {
              const isSelected = dim.id === selectedDimId;
              const isNeedsHuman = dim.status === "needs_human";

              return (
                <div
                  key={dim.id}
                  onClick={() => setSelectedDimId(dim.id)}
                  className={`p-3.5 cursor-pointer flex items-center justify-between text-xs transition-colors ${
                    isSelected
                      ? "bg-cyan-950/20 border-l-2 border-cyan-400"
                      : isNeedsHuman
                      ? "bg-amber-950/10 hover:bg-amber-950/20"
                      : "hover:bg-slate-800/40"
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white">{dim.name}</span>
                      <span className="font-mono text-[10px] text-slate-400">({dim.id})</span>
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono">
                      Type: {dim.type} • Tol: +{dim.tol_plus} / -{dim.tol_minus}
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="font-mono text-sm font-bold text-slate-100">
                      {dim.value !== null ? `${dim.value} ${dim.unit}` : "NOT FOUND"}
                    </span>
                    {dim.status === "verified_auto" ? (
                      <span className="w-2 h-2 rounded-full bg-emerald-400" title="Verified Auto" />
                    ) : dim.status === "human_confirmed" ? (
                      <span className="w-2 h-2 rounded-full bg-cyan-400" title="Human Confirmed" />
                    ) : (
                      <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" title="Needs Human Input" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
