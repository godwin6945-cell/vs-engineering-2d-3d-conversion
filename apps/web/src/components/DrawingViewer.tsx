"use client";

import React, { useState, useRef } from "react";
import { DimensionSpec } from "@/types/spec";
import { ZoomIn, ZoomOut, RotateCcw, Maximize2 } from "lucide-react";

interface DrawingViewerProps {
  imageUrl?: string;
  dimensions: DimensionSpec[];
  selectedDimId: string | null;
  onSelectDimension: (id: string) => void;
  className?: string;
}

export function DrawingViewer({
  imageUrl,
  dimensions,
  selectedDimId,
  onSelectDimension,
  className = "",
}: DrawingViewerProps) {
  const [scale, setScale] = useState(1.0);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setScale((s) => Math.min(s * 1.25, 4.0));
  const handleZoomOut = () => setScale((s) => Math.max(s / 1.25, 0.5));
  const handleReset = () => {
    setScale(1.0);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).dataset.bbox) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    setScale((s) => Math.max(0.5, Math.min(4.0, s * zoomFactor)));
  };

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onWheel={handleWheel}
      className={`relative flex-1 bg-white overflow-hidden select-none flex items-center justify-center cursor-grab active:cursor-grabbing ${className}`}
    >
      {/* Background Engineering Blueprint Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-40"
        style={{
          backgroundImage:
            "linear-gradient(to right, #e2e8f0 1px, transparent 1px), linear-gradient(to bottom, #e2e8f0 1px, transparent 1px)",
          backgroundSize: "24px 24px",
        }}
      />

      {/* Floating Canvas Controls */}
      <div className="absolute top-4 left-4 z-30 flex items-center gap-1.5 p-1 rounded-md bg-white/95 backdrop-blur border border-slate-300 shadow-sm">
        <button
          onClick={handleZoomIn}
          title="Zoom In (+)"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700 transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out (-)"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700 transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          title="Reset View"
          className="p-1.5 rounded hover:bg-slate-100 text-slate-700 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <div className="w-[1px] h-4 bg-slate-300 my-auto" />
        <span className="px-2 font-mono text-[11px] font-bold text-slate-700">
          {(scale * 100).toFixed(0)}%
        </span>
      </div>

      {/* Drawing Coordinate Frame */}
      <div
        className="relative transition-transform duration-75 origin-center"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
        }}
      >
        {/* Synthetic 2D Vector CAD Drawing Canvas */}
        <div className="w-[620px] h-[480px] bg-slate-50 border-2 border-slate-400 rounded relative shadow-sm overflow-hidden">
          {/* Engineering Drawing Border & Title Block */}
          <div className="absolute inset-2 border border-slate-300 pointer-events-none" />

          {/* Title Block Bottom Right */}
          <div className="absolute bottom-2 right-2 border-t border-l border-slate-300 bg-white/90 p-2 font-mono text-[10px] text-slate-700 leading-tight">
            <div className="font-bold text-slate-900">ALPHA PRECISION WORKS</div>
            <div>DWG NO: DWG-SYN-FLG-01</div>
            <div>SCALE: 1:1 • UNIT: MM • ISO 2768-m</div>
          </div>

          {/* Drawing Geometry Projections */}
          <svg className="w-full h-full pointer-events-none" viewBox="0 0 620 480">
            {/* Center crosshairs */}
            <line x1="310" y1="40" x2="310" y2="440" stroke="#94a3b8" strokeDasharray="6,4" strokeWidth="1" />
            <line x1="40" y1="240" x2="580" y2="240" stroke="#94a3b8" strokeDasharray="6,4" strokeWidth="1" />

            {/* Front View Projection - Flange Outer Contour */}
            <circle cx="310" cy="240" r="140" fill="#f8fafc" stroke="#1e293b" strokeWidth="2.5" />

            {/* Pitch Circle Diameter (PCD) */}
            <circle cx="310" cy="240" r="95" fill="none" stroke="#64748b" strokeDasharray="4,4" strokeWidth="1.2" />

            {/* Central Through Bore */}
            <circle cx="310" cy="240" r="45" fill="#e2e8f0" stroke="#1e293b" strokeWidth="2" />

            {/* 4 Bolt Holes at 90 deg intervals */}
            <circle cx="310" cy="145" r="14" fill="#ffffff" stroke="#1e293b" strokeWidth="1.8" />
            <circle cx="310" cy="335" r="14" fill="#ffffff" stroke="#1e293b" strokeWidth="1.8" />
            <circle cx="215" cy="240" r="14" fill="#ffffff" stroke="#1e293b" strokeWidth="1.8" />
            <circle cx="405" cy="240" r="14" fill="#ffffff" stroke="#1e293b" strokeWidth="1.8" />

            {/* Dimension Extension & Leader Lines */}
            <line x1="310" y1="100" x2="310" y2="70" stroke="#475569" strokeWidth="1" />
            <line x1="170" y1="240" x2="140" y2="240" stroke="#475569" strokeWidth="1" />
            <line x1="450" y1="240" x2="480" y2="240" stroke="#475569" strokeWidth="1" />
          </svg>

          {/* Interactive Normalized Bounding Box Overlays */}
          {dimensions.map((dim) => {
            if (!dim.bbox) return null;
            const isSelected = dim.id === selectedDimId;
            const isNeedsHuman = dim.status === "needs_human";

            const left = `${dim.bbox.x_min * 100}%`;
            const top = `${dim.bbox.y_min * 100}%`;
            const width = `${(dim.bbox.x_max - dim.bbox.x_min) * 100}%`;
            const height = `${(dim.bbox.y_max - dim.bbox.y_min) * 100}%`;

            return (
              <div
                key={dim.id}
                data-bbox="true"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectDimension(dim.id);
                }}
                style={{ left, top, width, height }}
                className={`absolute transition-all cursor-pointer rounded-xs flex items-center justify-center font-mono text-[10px] font-bold ${
                  isSelected
                    ? "border-2 border-sky-600 bg-sky-500/20 shadow-md ring-2 ring-sky-300"
                    : isNeedsHuman
                    ? "border-2 border-dashed border-amber-600 bg-amber-500/15 hover:bg-amber-500/25 animate-pulse"
                    : "border border-emerald-600 bg-emerald-500/10 hover:bg-emerald-500/20"
                }`}
              >
                {/* Floating Dimension Callout Badge */}
                <div
                  className={`absolute -top-6 px-1.5 py-0.5 rounded text-[10px] whitespace-nowrap shadow-xs font-mono font-bold pointer-events-none ${
                    isSelected
                      ? "bg-sky-700 text-white"
                      : isNeedsHuman
                      ? "bg-amber-600 text-white"
                      : "bg-emerald-700 text-white"
                  }`}
                >
                  {dim.value !== null ? `${dim.value}${dim.unit}` : "?"} [{dim.id}]
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
