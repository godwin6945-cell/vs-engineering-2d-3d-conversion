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
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium tracking-wide bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 ${className}`}
        >
          {showIcon && <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
          VERIFIED AUTO
        </span>
      );
    case "human_confirmed":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium tracking-wide bg-cyan-950/80 text-cyan-300 border border-cyan-700/60 ${className}`}
        >
          {showIcon && <UserCheck className="w-3 h-3 text-cyan-400" />}
          CONFIRMED
        </span>
      );
    case "human_entered":
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium tracking-wide bg-sky-950/80 text-sky-300 border border-sky-700/60 ${className}`}
        >
          {showIcon && <Edit2 className="w-3 h-3 text-sky-400" />}
          HUMAN ENTERED
        </span>
      );
    case "needs_human":
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-mono font-medium tracking-wide bg-amber-950/80 text-amber-300 border border-amber-600/70 shadow-[0_0_8px_rgba(245,158,11,0.2)] ${className}`}
        >
          {showIcon && <AlertCircle className="w-3 h-3 text-amber-400 animate-pulse" />}
          NEEDS ATTENTION
        </span>
      );
  }
}
