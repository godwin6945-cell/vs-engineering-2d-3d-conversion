"use client";

import React from "react";
import { DimensionSpec } from "@/types/spec";
import { StatusBadge } from "./StatusBadge";
import { ChevronRight, Edit3, Compass } from "lucide-react";

interface DimensionRowProps {
  dimension: DimensionSpec;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onEditClick?: (dim: DimensionSpec) => void;
}

export function DimensionRow({
  dimension,
  isSelected,
  onSelect,
  onEditClick,
}: DimensionRowProps) {
  const isNeedsHuman = dimension.status === "needs_human";
  const hasValue = dimension.value !== null && dimension.value !== undefined;

  return (
    <div
      onClick={() => onSelect(dimension.id)}
      role="row"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(dimension.id);
        }
      }}
      className={`p-3.5 cursor-pointer flex items-center justify-between transition-all select-none border-b border-[#1c2734] outline-none ${
        isSelected
          ? "bg-cyan-950/30 border-l-4 border-l-cyan-400 pl-2.5"
          : isNeedsHuman
          ? "bg-amber-950/15 hover:bg-amber-950/25 border-l-2 border-l-amber-500/50"
          : "hover:bg-[#151e2a] border-l-2 border-l-transparent"
      }`}
    >
      {/* Left Info: Name, ID, Type, Tolerance */}
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span
            className={`font-semibold text-xs tracking-wide ${
              isSelected ? "text-cyan-200" : isNeedsHuman ? "text-amber-100" : "text-slate-100"
            }`}
          >
            {dimension.name}
          </span>
          <span className="font-mono text-[10px] text-slate-400">
            [{dimension.id}]
          </span>
          <span className="px-1.5 py-0.2 rounded text-[9px] font-mono uppercase bg-slate-800 text-slate-300">
            {dimension.view}
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
          <span className="capitalize">{dimension.type}</span>
          <span>•</span>
          <span>
            +{dimension.tol_plus} / -{dimension.tol_minus}
          </span>
          {dimension.source !== "printed" && (
            <>
              <span>•</span>
              <span className="text-amber-400 font-semibold uppercase text-[10px]">
                {dimension.source}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Right Info: Nominal Value, Status Badge & Edit Indicator */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div
            className={`font-mono text-sm font-bold tracking-tight ${
              hasValue
                ? isSelected
                  ? "text-cyan-300"
                  : "text-slate-100"
                : "text-amber-400 font-semibold italic text-xs"
            }`}
          >
            {hasValue ? `${dimension.value} ${dimension.unit}` : "NOT SPECIFIED"}
          </div>
          <div className="text-[10px] font-mono text-slate-500">
            conf: {(dimension.confidence * 100).toFixed(0)}%
          </div>
        </div>

        <StatusBadge status={dimension.status} showIcon={false} />

        {isSelected && (
          <ChevronRight className="w-4 h-4 text-cyan-400 animate-pulse" />
        )}
      </div>
    </div>
  );
}
