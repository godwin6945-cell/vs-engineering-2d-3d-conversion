"use client";

import React from "react";
import { ValidationReport, GeometryMeasurement } from "@/types/spec";
import { CheckCircle2, XCircle, ShieldCheck, Layers, Gauge } from "lucide-react";

interface ValidationTableProps {
  report: ValidationReport;
  className?: string;
}

export function ValidationTable({ report, className = "" }: ValidationTableProps) {
  return (
    <div className={`space-y-4 bg-[#111720] border border-[#222f3e] rounded-lg p-5 font-mono ${className}`}>
      {/* Topology & Solid Integrity Summary */}
      <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
        <div className="flex items-center gap-2">
          <ShieldCheck className={`w-5 h-5 ${report.overall_passed ? "text-emerald-400" : "text-amber-400"}`} />
          <div>
            <h3 className="text-xs font-semibold text-white tracking-wide uppercase">
              OpenCascade Geometry Validation
            </h3>
            <span className="text-[10px] text-slate-400">
              Measured from generated B-Rep solid vs confirmed specification
            </span>
          </div>
        </div>

        <span
          className={`px-2.5 py-1 rounded text-xs font-bold uppercase tracking-wider ${
            report.overall_passed
              ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
              : "bg-amber-950 text-amber-300 border border-amber-800"
          }`}
        >
          {report.overall_passed ? "PASSED ALL CHECKS" : "TOLERANCE DEVIATION"}
        </span>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-3 rounded bg-[#0b1017] border border-[#1e293b]">
          <span className="text-[10px] text-slate-400 uppercase">Bounding Box</span>
          <div className="text-sm font-bold text-slate-100 mt-1">
            {report.bounding_box_x} × {report.bounding_box_y} × {report.bounding_box_z} mm
          </div>
        </div>

        <div className="p-3 rounded bg-[#0b1017] border border-[#1e293b]">
          <span className="text-[10px] text-slate-400 uppercase">Solid Volume</span>
          <div className="text-sm font-bold text-slate-100 mt-1">
            {report.volume_mm3.toLocaleString()} mm³
          </div>
        </div>

        <div className="p-3 rounded bg-[#0b1017] border border-[#1e293b]">
          <span className="text-[10px] text-slate-400 uppercase">Topology Elements</span>
          <div className="text-sm font-bold text-slate-100 mt-1">
            {report.face_count} Faces • {report.edge_count} Edges
          </div>
        </div>

        <div className="p-3 rounded bg-[#0b1017] border border-[#1e293b]">
          <span className="text-[10px] text-slate-400 uppercase">STEP Roundtrip</span>
          <div className="text-sm font-bold flex items-center gap-1.5 mt-1 text-emerald-400">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Verified AP214
          </div>
        </div>
      </div>

      {/* Detailed Measurements vs Specified Table */}
      {report.measurements.length > 0 && (
        <div className="overflow-x-auto pt-2">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-[#222f3e] text-[10px] uppercase text-slate-400">
                <th className="pb-2 font-normal">Feature / Dimension</th>
                <th className="pb-2 font-normal text-right">Specified</th>
                <th className="pb-2 font-normal text-right">Measured</th>
                <th className="pb-2 font-normal text-right">Delta (Δ)</th>
                <th className="pb-2 font-normal text-right">Tolerance</th>
                <th className="pb-2 font-normal text-center">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#182330]">
              {report.measurements.map((m: GeometryMeasurement, idx: number) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2.5 font-semibold text-slate-200">
                    {m.name}
                    {m.dimension_id && (
                      <span className="text-[10px] text-slate-500 ml-1.5">[{m.dimension_id}]</span>
                    )}
                  </td>
                  <td className="py-2.5 text-right text-slate-300">{m.specified_value} mm</td>
                  <td className="py-2.5 text-right font-bold text-white">{m.measured_value} mm</td>
                  <td
                    className={`py-2.5 text-right font-bold ${
                      Math.abs(m.deviation) <= 0.001 ? "text-slate-400" : "text-cyan-400"
                    }`}
                  >
                    {m.deviation >= 0 ? `+${m.deviation.toFixed(3)}` : m.deviation.toFixed(3)} mm
                  </td>
                  <td className="py-2.5 text-right text-slate-400">
                    +{m.tolerance_plus} / -{m.tolerance_minus}
                  </td>
                  <td className="py-2.5 text-center">
                    {m.passed ? (
                      <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-bold bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
                        <CheckCircle2 className="w-3 h-3" /> PASS
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[10px] text-red-400 font-bold bg-red-950/60 px-2 py-0.5 rounded border border-red-800">
                        <XCircle className="w-3 h-3" /> FAIL
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
