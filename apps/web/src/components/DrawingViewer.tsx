"use client";

import React, { useState, useRef, useEffect } from "react";
import { DimensionSpec } from "@/types/spec";
import { ZoomIn, ZoomOut, RotateCcw, Maximize2, Move } from "lucide-react";

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
    // Only drag when clicking background, not bounding box directly
    if ((e.target as HTMLElement).dataset.bbox) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
  };

  const handleMouseUp = () => setIsDragging(false);

  // Wheel zoom
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
      className={`relative flex-1 bg-[#090d12] overflow-hidden select-none flex items-center justify-center cursor-grab active:cursor-grabbing ${className}`}
    >
      {/* Background Engineering Grid */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage:
            "radial-gradient(#334155 1px, transparent 1px), radial-gradient(#1e293b 1px, #090d12 1px)",
          backgroundSize: "24px 24px",
          backgroundPosition: "0 0, 12px 12px",
        }}
      />

      {/* Floating Canvas Controls */}
      <div className="absolute top-4 left-4 z-30 flex items-center gap-1.5 p-1 rounded-lg bg-[#111720]/90 backdrop-blur border border-[#222f3e] shadow-xl">
        <button
          onClick={handleZoomIn}
          title="Zoom In (+)"
          className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out (-)"
          className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <div className="w-[1px] h-4 bg-slate-700 mx-0.5" />
        <button
          onClick={handleReset}
          title="Reset View"
          className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <span className="text-[10px] font-mono text-slate-400 px-2 select-none">
          {Math.round(scale * 100)}%
        </span>
      </div>

      {/* Main Drawing Container with Pan & Zoom transform */}
      <div
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
          transition: isDragging ? "none" : "transform 0.15s ease-out",
        }}
        className="relative w-full max-w-3xl aspect-[4/3] bg-slate-950/80 border border-[#222f3e] rounded-lg shadow-2xl flex items-center justify-center p-4"
      >
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="Engineering Drawing"
            className="w-full h-full object-contain pointer-events-none"
          />
        ) : (
          /* High-fidelity Vector Schematic for precision part */
          <svg className="w-full h-full p-8" viewBox="0 0 500 380">
            {/* Title Block Border */}
            <rect
              x="20"
              y="20"
              width="460"
              height="340"
              fill="none"
              stroke="#1e293b"
              strokeWidth="1.5"
            />
            {/* Title Block Box Bottom Right */}
            <rect
              x="300"
              y="300"
              width="180"
              height="60"
              fill="#0b1017"
              stroke="#334155"
              strokeWidth="1"
            />
            <text x="310" y="320" fill="#94a3b8" fontSize="10" fontFamily="monospace">
              DWG: SK2S-FLANGE-01
            </text>
            <text x="310" y="335" fill="#cbd5e1" fontSize="11" fontFamily="sans-serif" fontWeight="bold">
              PRECISION FLANGE
            </text>
            <text x="310" y="350" fill="#64748b" fontSize="9" fontFamily="monospace">
              STANDARD: ISO 2768-m | 1:1
            </text>

            {/* Part Silhouette (Flange with central bore + bolt pattern) */}
            <rect
              x="70"
              y="60"
              width="360"
              height="220"
              rx="12"
              fill="#0f172a"
              stroke="#475569"
              strokeWidth="2"
            />
            {/* Center Boss Protrusion */}
            <circle
              cx="250"
              cy="170"
              r="70"
              fill="#1e293b"
              stroke="#64748b"
              strokeWidth="1.5"
            />
            {/* Center Through Hole */}
            <circle
              cx="250"
              cy="170"
              r="35"
              fill="#090d12"
              stroke="#94a3b8"
              strokeWidth="2"
            />
            {/* 4x Bolt Hole Pattern */}
            <circle cx="120" cy="100" r="12" fill="#090d12" stroke="#94a3b8" strokeWidth="1.5" />
            <circle cx="380" cy="100" r="12" fill="#090d12" stroke="#94a3b8" strokeWidth="1.5" />
            <circle cx="120" cy="240" r="12" fill="#090d12" stroke="#94a3b8" strokeWidth="1.5" />
            <circle cx="380" cy="240" r="12" fill="#090d12" stroke="#94a3b8" strokeWidth="1.5" />

            {/* PCD Pitch Circle Dash */}
            <circle
              cx="250"
              cy="170"
              r="100"
              fill="none"
              stroke="#334155"
              strokeWidth="1"
              strokeDasharray="6 4"
            />

            {/* Centerlines */}
            <line x1="50" y1="170" x2="450" y2="170" stroke="#334155" strokeWidth="1" strokeDasharray="8 4" />
            <line x1="250" y1="40" x2="250" y2="300" stroke="#334155" strokeWidth="1" strokeDasharray="8 4" />
          </svg>
        )}

        {/* Interactive Dimension Bounding Box Overlays */}
        {dimensions.map((dim) => {
          if (!dim.bbox) return null;
          const isSelected = dim.id === selectedDimId;
          const isVerified =
            (dim.status === "verified_auto" ||
              dim.status === "human_confirmed" ||
              dim.status === "human_entered") &&
            dim.value !== null;

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
              className={`absolute cursor-pointer border-2 transition-all flex items-center justify-center rounded-sm ${
                isSelected
                  ? "border-cyan-400 bg-cyan-500/25 shadow-[0_0_16px_rgba(6,182,212,0.6)] z-30 scale-105"
                  : isVerified
                  ? "border-emerald-500/70 bg-emerald-500/10 hover:border-emerald-400 z-10"
                  : "border-amber-400/90 bg-amber-500/20 hover:border-amber-300 z-20 animate-pulse"
              }`}
            >
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded font-bold shadow-md ${
                  isSelected
                    ? "bg-cyan-400 text-slate-950 ring-2 ring-cyan-200"
                    : isVerified
                    ? "bg-emerald-950 text-emerald-300 border border-emerald-700"
                    : "bg-amber-950 text-amber-200 border border-amber-600"
                }`}
              >
                {dim.value !== null ? `${dim.value}` : "???"}
              </span>
            </div>
          );
        })}
      </div>

      {/* Bottom Hint */}
      <div className="absolute bottom-4 left-6 z-20 flex items-center gap-2 text-[11px] text-slate-400 font-mono bg-[#111720]/80 backdrop-blur px-3 py-1.5 rounded-md border border-[#222f3e]">
        <Move className="w-3.5 h-3.5 text-cyan-400" />
        <span>Drag to pan • Scroll to zoom • Click bounding box to select</span>
      </div>
    </div>
  );
}
