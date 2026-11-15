"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { DimensionSpec, DimensionStatus, DrawingSanityCheckResult } from "@/types/spec";
import { DrawingViewer } from "./DrawingViewer";
import { DimensionRow } from "./DimensionRow";
import { EvidenceChips } from "./EvidenceChips";
import { ReviewProgress } from "./ReviewProgress";
import { SanityChecksPanel } from "./SanityChecksPanel";
import { StatusBadge } from "./StatusBadge";
import { updateJobDimension } from "@/lib/api";
import {
  Check,
  ShieldCheck,
  AlertTriangle,
  RotateCcw,
  Info,
  CornerDownLeft,
} from "lucide-react";

interface ReviewWorkspaceProps {
  jobId: string;
  initialDimensions: DimensionSpec[];
  initialSanityChecks?: DrawingSanityCheckResult[];
  drawingImageUrl?: string;
  onGenerateCad?: () => void;
}

export function ReviewWorkspace({
  jobId,
  initialDimensions,
  initialSanityChecks = [],
  drawingImageUrl,
  onGenerateCad,
}: ReviewWorkspaceProps) {
  const router = useRouter();
  const [dimensions, setDimensions] = useState<DimensionSpec[]>(initialDimensions);
  const [selectedDimId, setSelectedDimId] = useState<string | null>(
    initialDimensions.find((d) => d.status === "needs_human")?.id ||
      initialDimensions[0]?.id ||
      null
  );

  // Edit fields for selected dimension
  const [editValue, setEditValue] = useState<string>("");
  const [editTolPlus, setEditTolPlus] = useState<string>("0.0");
  const [editTolMinus, setEditTolMinus] = useState<string>("0.0");
  const [editNotes, setEditNotes] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  const inputRef = useRef<HTMLInputElement>(null);

  const selectedDim = dimensions.find((d) => d.id === selectedDimId);

  // Populate edit fields when selection changes
  useEffect(() => {
    if (selectedDim) {
      setEditValue(selectedDim.value !== null && selectedDim.value !== undefined ? String(selectedDim.value) : "");
      setEditTolPlus(String(selectedDim.tol_plus || 0.0));
      setEditTolMinus(String(selectedDim.tol_minus || 0.0));
      setEditNotes(selectedDim.notes || "");
    }
  }, [selectedDimId, selectedDim]);

  // Global Keyboard Navigation (J/K to move, Enter to confirm, E to edit, Esc to cancel)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        if (e.key === "Enter") {
          e.preventDefault();
          handleConfirmCurrent();
        } else if (e.key === "Escape") {
          inputRef.current?.blur();
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
        inputRef.current?.focus();
        inputRef.current?.select();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [dimensions, selectedDimId, editValue, editTolPlus, editTolMinus, editNotes]);

  // Save / Confirm handler
  const handleConfirmCurrent = async () => {
    if (!selectedDimId) return;
    const num = parseFloat(editValue);
    if (isNaN(num)) return;

    const tolPlusNum = parseFloat(editTolPlus) || 0.0;
    const tolMinusNum = parseFloat(editTolMinus) || 0.0;

    // Optimistic local update
    const updatedDimensions = dimensions.map((d) => {
      if (d.id === selectedDimId) {
        return {
          ...d,
          value: num,
          tol_plus: tolPlusNum,
          tol_minus: tolMinusNum,
          notes: editNotes,
          status: "human_confirmed" as DimensionStatus,
        };
      }
      return d;
    });

    setDimensions(updatedDimensions);

    // Call API in background
    try {
      setIsSaving(true);
      await updateJobDimension(jobId, selectedDimId, {
        value: num,
        tol_plus: tolPlusNum,
        tol_minus: tolMinusNum,
        status: "human_confirmed",
        notes: editNotes,
      });
    } catch (err) {
      // Backend API sync caught or mock fallback
    } finally {
      setIsSaving(false);
    }

    // Auto-advance to next dimension requiring attention
    const currentIndex = dimensions.findIndex((d) => d.id === selectedDimId);
    const nextNeedsHuman =
      dimensions.find((d, i) => i > currentIndex && d.status === "needs_human") ||
      dimensions.find((d) => d.status === "needs_human");

    if (nextNeedsHuman) {
      setSelectedDimId(nextNeedsHuman.id);
    }
  };

  const handleGenerateModel = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setIsGenerating(false);
      router.push(`/jobs/${jobId}/model`);
    }, 700);
  };

  // Group dimensions: Needs Human Attention first, then Verified
  const needsHumanList = dimensions.filter((d) => d.status === "needs_human");
  const verifiedList = dimensions.filter((d) => d.status !== "needs_human");

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] bg-slate-50 text-slate-900 overflow-hidden font-sans">
      {/* Top Review Bar & Progress */}
      <div className="h-16 border-b border-slate-200 bg-white px-6 flex items-center justify-between z-20 shrink-0 shadow-xs">
        <div className="flex items-center gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-bold text-slate-900 tracking-wide">
                Engineering Drawing Review Workspace
              </h1>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                JOB: {jobId.slice(0, 8)}
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-mono mt-0.5">
              Shortcuts: <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">J</kbd>/<kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">K</kbd> navigate • <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">Enter</kbd> confirm • <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">E</kbd> edit • <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">Esc</kbd> cancel
            </p>
          </div>
        </div>

        {/* Verification Progress Bar & Gated Model Generation */}
        <ReviewProgress
          dimensions={dimensions}
          onGenerateClick={handleGenerateModel}
          isGenerating={isGenerating}
        />
      </div>

      {/* Split Workspace View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Interactive 2D Drawing Canvas */}
        <div className="flex-1 flex flex-col relative border-r border-slate-200 overflow-hidden bg-white">
          <DrawingViewer
            imageUrl={drawingImageUrl}
            dimensions={dimensions}
            selectedDimId={selectedDimId}
            onSelectDimension={(id) => setSelectedDimId(id)}
          />

          {/* Sanity Rules Drawer at bottom of drawing viewer */}
          {initialSanityChecks.length > 0 && (
            <div className="p-3 bg-slate-50 border-t border-slate-200">
              <SanityChecksPanel
                checks={initialSanityChecks}
                onSelectDimension={(id) => setSelectedDimId(id)}
              />
            </div>
          )}
        </div>

        {/* Right Pane: Dimension Verification Table & Detail Editor */}
        <div className="w-[490px] flex flex-col bg-white border-l border-slate-200 overflow-hidden shrink-0">
          {/* Selected Dimension Detail & Edit Inspector */}
          {selectedDim ? (
            <div className="p-4 border-b border-slate-200 bg-slate-50/70 space-y-3.5 shadow-xs shrink-0">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-[10px] uppercase font-mono font-bold tracking-wider text-slate-500">
                    Selected Dimension [{selectedDim.id}]
                  </div>
                  <div className="text-sm font-bold text-slate-900 tracking-wide">
                    {selectedDim.name}
                  </div>
                </div>
                <StatusBadge status={selectedDim.status} />
              </div>

              {/* Evidence Chips: Claude Pass A, Claude Pass B, RapidOCR */}
              <EvidenceChips evidence={selectedDim.evidence} unit={selectedDim.unit} />

              {/* Form Input for Nominal Value & Tolerances */}
              <div className="space-y-2 bg-white p-3.5 rounded-lg border border-slate-200 shadow-2xs">
                <label className="text-xs font-bold text-slate-800 flex items-center justify-between">
                  <span>
                    {selectedDim.value === null
                      ? "Value not found on drawing. Enter nominal:"
                      : "Nominal Dimension & Tolerances:"}
                  </span>
                  <span className="text-[10px] text-sky-800 font-mono font-bold">
                    Unit: {selectedDim.unit}
                  </span>
                </label>

                <div className="grid grid-cols-3 gap-2">
                  {/* Nominal Value */}
                  <div className="col-span-1">
                    <span className="text-[10px] font-mono text-slate-500 font-bold">Nominal</span>
                    <input
                      ref={inputRef}
                      type="number"
                      step="0.01"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      placeholder="e.g. 50.0"
                      className="w-full mt-1 px-2.5 py-1.5 rounded-md bg-white border border-slate-300 text-sm font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 font-bold"
                    />
                  </div>

                  {/* +Tolerance */}
                  <div>
                    <span className="text-[10px] font-mono text-slate-500 font-bold">+Tol</span>
                    <input
                      type="number"
                      step="0.01"
                      value={editTolPlus}
                      onChange={(e) => setEditTolPlus(e.target.value)}
                      className="w-full mt-1 px-2.5 py-1.5 rounded-md bg-white border border-slate-300 text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  {/* -Tolerance */}
                  <div>
                    <span className="text-[10px] font-mono text-slate-500 font-bold">-Tol</span>
                    <input
                      type="number"
                      step="0.01"
                      value={editTolMinus}
                      onChange={(e) => setEditTolMinus(e.target.value)}
                      className="w-full mt-1 px-2.5 py-1.5 rounded-md bg-white border border-slate-300 text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                </div>

                {/* Confirm Action Button */}
                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] font-mono text-slate-500">
                    Press <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 text-slate-700 rounded font-bold">Enter</kbd> to lock & next
                  </span>
                  <button
                    onClick={handleConfirmCurrent}
                    disabled={isSaving}
                    className="px-4 py-2 rounded-md bg-sky-700 hover:bg-sky-800 text-white font-mono text-xs font-bold flex items-center gap-1.5 transition-colors shadow-xs cursor-pointer"
                  >
                    <Check className="w-4 h-4" />
                    {isSaving ? "Locking..." : "Confirm Dimension"}
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-slate-500 text-xs font-mono">
              Select a dimension to inspect evidence and edit parameters.
            </div>
          )}

          {/* Grouped Dimension Table Header & List */}
          <div className="flex-1 overflow-y-auto">
            {/* Section 1: Needs Human Attention */}
            {needsHumanList.length > 0 && (
              <div>
                <div className="sticky top-0 z-10 px-4 py-2.5 bg-amber-50 border-y border-amber-200 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-amber-900">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    <span>NEEDS HUMAN ATTENTION ({needsHumanList.length})</span>
                  </div>
                  <span className="text-[10px] font-mono font-semibold text-amber-800">
                    Resolve to unlock CAD
                  </span>
                </div>
                {needsHumanList.map((dim) => (
                  <DimensionRow
                    key={dim.id}
                    dimension={dim}
                    isSelected={dim.id === selectedDimId}
                    onSelect={(id) => setSelectedDimId(id)}
                  />
                ))}
              </div>
            )}

            {/* Section 2: Verified Dimensions */}
            <div>
              <div className="sticky top-0 z-10 px-4 py-2.5 bg-slate-100 border-y border-slate-200 flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs font-mono font-bold text-slate-800">
                  <Check className="w-3.5 h-3.5 text-emerald-600" />
                  <span>VERIFIED SPECIFICATIONS ({verifiedList.length})</span>
                </div>
                <span className="text-[10px] font-mono font-semibold text-emerald-800">
                  Ready for Solid Kernel
                </span>
              </div>
              {verifiedList.map((dim) => (
                <DimensionRow
                  key={dim.id}
                  dimension={dim}
                  isSelected={dim.id === selectedDimId}
                  onSelect={(id) => setSelectedDimId(id)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
