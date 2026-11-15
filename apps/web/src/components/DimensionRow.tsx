"use client";

import React from "react";
import { DimensionSpec } from "@/types/spec";
import { StatusBadge } from "./StatusBadge";
import { ChevronRight, Edit3 } from "lucide-react";

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
      className={`p-3.5 cursor-pointer flex items-center justify-between transition-all select-none border-b border-slate-200 outline-none ${
        isSelected
          ? "bg-sky-50/80 border-l-4 border-l-sky-600 pl-2.5"
          : isNeedsHuman
          ? "bg-amber-50/60 hover:bg-amber-50/90 border-l-4 border-l-amber-500 pl-2.5"
          : "hover:bg-slate-50 border-l-4 border-l-transparent pl-2.5"
      }`}
    >
      {/* Left Info: Name, ID, Type, Tolerance */}
      <div className="space-y-1">
        <div className="flex items-center gap-2">
          <span
            className={`font-bold text-xs tracking-wide ${
              isSelected ? "text-sky-900" : isNeedsHuman ? "text-amber-900" : "text-slate-900"
            }`}
          >
            {dimension.name}
          </span>
          <span className="font-mono text-[10px] text-slate-500 font-semibold">
            [{dimension.id}]
          </span>
          <span className="px-1.5 py-0.2 rounded text-[9px] font-mono uppercase bg-slate-100 text-slate-700 border border-slate-200">
            {dimension.view}
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-500">
          <span>Type: {dimension.type}</span>
          <span>•</span>
          <span>
            Tol: +{dimension.tol_plus || 0.0} / -{dimension.tol_minus || 0.0}
          </span>
          {dimension.source === "missing" && (
            <>
              <span>•</span>
              <span className="text-amber-700 font-bold">Omitted on 2D view</span>
            </>
          )}
        </div>
      </div>

      {/* Right Info: Numeric Value Callout & Status */}
      <div className="flex items-center gap-3 text-right">
        <div>
          <div
            className={`text-sm font-mono font-bold ${
              hasValue
                ? isSelected
                  ? "text-sky-700"
                  : isNeedsHuman
                  ? "text-amber-800"
                  : "text-slate-900"
                : "text-amber-700 italic text-xs"
            }`}
          >
            {hasValue ? `${dimension.value?.toFixed(2)} ${dimension.unit}` : "Missing Value"}
          </div>
          <div className="mt-0.5">
            <StatusBadge status={dimension.status} />
          </div>
        </div>

        <ChevronRight
          className={`w-4 h-4 transition-transform ${
            isSelected ? "text-sky-700 translate-x-0.5" : "text-slate-400"
          }`}
        />
      </div>
    </div>
  );
}
