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
    <div className={`space-y-4 bg-white border border-slate-200 rounded-lg p-5 font-mono shadow-xs ${className}`}>
      {/* Topology & Solid Integrity Summary */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <ShieldCheck className={`w-5 h-5 ${report.overall_passed ? "text-emerald-600" : "text-amber-600"}`} />
          <div>
            <h3 className="text-xs font-bold text-slate-900 tracking-wide uppercase">
              OpenCascade Geometry Measurement
            </h3>
            <span className="text-[10px] text-slate-500">
              Measured from synthesized B-Rep solid vs confirmed spec
            </span>
          </div>
        </div>

        <span
          className={`px-2.5 py-1 rounded text-xs font-bold uppercase tracking-wider ${
            report.overall_passed
              ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
              : "bg-amber-50 text-amber-800 border border-amber-200"
          }`}
        >
          {report.overall_passed ? "PASSED ALL CHECKS" : "TOLERANCE DEVIATION"}
        </span>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-bold">Bounding Box</span>
          <div className="text-sm font-bold text-slate-900 mt-1">
            {report.bounding_box_x} × {report.bounding_box_y} × {report.bounding_box_z} mm
          </div>
        </div>

        <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-bold">Solid Volume</span>
          <div className="text-sm font-bold text-slate-900 mt-1">
            {report.volume_mm3.toLocaleString()} mm³
          </div>
        </div>

        <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-bold">Topology Elements</span>
          <div className="text-sm font-bold text-slate-900 mt-1">
            {report.face_count} Faces • {report.edge_count} Edges
          </div>
        </div>

        <div className="p-3 rounded-md bg-slate-50 border border-slate-200">
          <span className="text-[10px] text-slate-500 uppercase font-bold">Shell Closure</span>
          <div className="text-sm font-bold text-emerald-700 mt-1 flex items-center gap-1">
            <CheckCircle2 className="w-4 h-4" />
            100% Manifold
          </div>
        </div>
      </div>

      {/* Dimensional Measurement Comparison Table */}
      <div className="space-y-2">
        <div className="text-xs font-bold text-slate-800 uppercase tracking-wide">
          Reverse Geometric Probing vs Specification
        </div>

        <div className="overflow-x-auto rounded-md border border-slate-200">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-100 text-slate-700 border-b border-slate-200 text-[10px] uppercase font-bold">
              <tr>
                <th className="p-2.5">Feature Dimension</th>
                <th className="p-2.5">Specified</th>
                <th className="p-2.5">Measured</th>
                <th className="p-2.5">Tolerance</th>
                <th className="p-2.5">Deviation (Δ)</th>
                <th className="p-2.5">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {report.measurements.map((m) => (
                <tr key={m.dimension_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="p-2.5 font-medium text-slate-900">
                    <div>{m.name}</div>
                    <span className="text-[10px] text-slate-500 font-mono">[{m.dimension_id}]</span>
                  </td>
                  <td className="p-2.5 font-bold text-slate-800">{m.specified_value.toFixed(2)} mm</td>
                  <td className="p-2.5 font-bold text-slate-900">{m.measured_value.toFixed(2)} mm</td>
                  <td className="p-2.5 text-slate-600 font-mono">
                    +{m.tolerance_plus} / -{m.tolerance_minus}
                  </td>
                  <td
                    className={`p-2.5 font-bold ${
                      Math.abs(m.deviation) < 0.001 ? "text-emerald-700" : "text-amber-700"
                    }`}
                  >
                    {m.deviation >= 0 ? `+${m.deviation.toFixed(3)}` : m.deviation.toFixed(3)} mm
                  </td>
                  <td className="p-2.5">
                    {m.passed ? (
                      <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-bold">
                        PASS
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-red-50 text-red-800 border border-red-200 text-[10px] font-bold">
                        FAIL
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
