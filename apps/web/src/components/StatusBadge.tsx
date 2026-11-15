"use client";

import React from "react";
import { DimensionStatus } from "@/types/spec";
import { CheckCircle2, AlertCircle, UserCheck, Edit2 } from "lucide-react";

interface StatusBadgeProps {
  status: DimensionStatus;
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({ status, className = "", showIcon = true }: StatusBadgeProps) {
  switch (status) {
    case "verified_auto":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide bg-emerald-50 text-emerald-800 border border-emerald-200 ${className}`}
        >
          {showIcon && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
          VERIFIED AUTO
        </span>
      );
    case "human_confirmed":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide bg-sky-50 text-sky-800 border border-sky-200 ${className}`}
        >
          {showIcon && <UserCheck className="w-3 h-3 text-sky-700" />}
          CONFIRMED
        </span>
      );
    case "human_entered":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide bg-slate-100 text-slate-800 border border-slate-300 ${className}`}
        >
          {showIcon && <Edit2 className="w-3 h-3 text-slate-600" />}
          HUMAN ENTERED
        </span>
      );
    case "needs_human":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wide bg-amber-50 text-amber-900 border border-amber-300 ${className}`}
        >
          {showIcon && <AlertCircle className="w-3 h-3 text-amber-600" />}
          NEEDS ATTENTION
        </span>
      );
  }
}
