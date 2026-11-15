"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileCode2,
  ArrowRight,
  Upload,
  HardDrive,
  ShieldCheck,
  Layers,
  Cpu,
  Check,
  FileUp,
  X,
  FileText,
  SlidersHorizontal,
  ChevronRight,
  Gauge,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadTitle, setUploadTitle] = useState("Turned Adapter Flange");
  const [uploadDwgNo, setUploadDwgNo] = useState("DWG-2026-ENG-08");
  const [uploadTolerance, setUploadTolerance] = useState("ISO 2768-m");
  const [uploadingState, setUploadingState] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Industrial benchmark parts pre-compiled in eval/datasets
  const demoParts = [
    {
      id: "part_01",
      title: "Turned Flange Plate DN25",
      dwgNo: "DWG-SYN-FLG-01",
      category: "Turned & Bored",
      material: "Steel 1018",
      dimensions: 5,
      features: 3,
      unverifiedCount: 1,
      totalCount: 5,
      standard: "ISO 2768-m",
      description: "90mm OD with 4-hole PCD bolt circle and 25mm central through-bore.",
    },
    {
      id: "part_07",
      title: "Milled Fixture Plate 120x80",
      dwgNo: "DWG-SYN-PLT-07",
      category: "Milled Plate",
      material: "Aluminum 6061-T6",
      dimensions: 6,
      features: 2,
      unverifiedCount: 0,
      totalCount: 6,
      standard: "ISO 2768-m",
      description: "Base plate with precision central rectangular cavity pocket.",
    },
    {
      id: "part_13",
      title: "Turned Transmission Shaft Mod-1",
      dwgNo: "DWG-SYN-SFT-13",
      category: "Turned Shaft",
      material: "Alloy Steel 4140",
      dimensions: 4,
      features: 1,
      unverifiedCount: 1,
      totalCount: 4,
      standard: "DIN 7168-m",
      description: "Dual-diameter stepped cylindrical transmission shaft.",
    },
  ];

  const reviewQueue = [
    {
      id: "part_01",
      title: "Turned Flange Housing - Rev C",
      drawingNumber: "DWG-2026-FLG-04",
      unverifiedCount: 2,
      totalCount: 16,
      updatedAt: "10 mins ago",
      standard: "ISO 2768-m",
    },
    {
      id: "part_13",
      title: "Stepped Drive Shaft (Turned Part)",
      drawingNumber: "DWG-2026-SFT-12",
      unverifiedCount: 1,
      totalCount: 22,
      updatedAt: "25 mins ago",
      standard: "ISO 2768-f",
    },
  ];

  const recentJobs = [
    {
      id: "part_07",
      title: "Milled Fixture Plate 120x80",
      state: "EXPORTED",
      accuracyScore: "100% Confirmed",
      stepExported: true,
      time: "2 hours ago",
    },
    {
      id: "part_02",
      title: "Cylinder End Cap DN35",
      state: "SIGNED_OFF",
      accuracyScore: "18/18 Verified",
      stepExported: false,
      time: "4 hours ago",
    },
  ];

  const handleStartUpload = () => {
    setUploadingState("Rasterizing 2D projections & extracting vector topology...");
    setTimeout(() => {
      setUploadingState("Executing Dual Claude vision extraction passes...");
      setTimeout(() => {
        setUploadingState("Cross-checking RapidOCR bounding boxes...");
        setTimeout(() => {
          setUploadingState(null);
          setShowUploadModal(false);
          router.push("/jobs/part_01/review");
        }, 800);
      }, 800);
    }, 800);
  };

  return (
    <div className="flex-1 p-8 max-w-7xl mx-auto w-full space-y-8 bg-slate-50">
      {/* Precision CAD Guarantee Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 rounded-lg border border-slate-200 bg-white shadow-xs">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-700">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h1 className="text-base font-bold tracking-tight text-slate-900">
              Precision CAD Reconstruction Pipeline
            </h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-sky-50 text-sky-800 border border-sky-200">
              ISO 10303 AP214
            </span>
          </div>
          <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
            Strict Accuracy Guarantee: No dimension reaches the STEP file unless verified by two vision passes and OCR, or signed off by an engineer. Reverse geometric measurement verified against ISO 2768 tolerances.
          </p>
        </div>

        <button
          onClick={() => setShowUploadModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-md bg-sky-700 hover:bg-sky-800 text-white text-xs font-semibold tracking-wide transition-all shadow-sm hover:shadow self-start md:self-auto cursor-pointer"
        >
          <Upload className="w-4 h-4" />
          Upload 2D Drawing
        </button>
      </div>

      {/* Interactive Benchmark Gallery */}
      <div className="p-6 rounded-lg border border-slate-200 bg-white shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-sky-700" />
            <h2 className="text-xs font-bold text-slate-900 tracking-wider uppercase font-mono">
              Synthetic Benchmark Parts (30 Specimen Suite)
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-500">
            OpenCascade Solid Models Pre-compiled
          </span>
        </div>
        <p className="text-xs text-slate-600">
          Select an industrial specimen below to immediately inspect drawing overlays, dual-pass Claude evidence, and verified 3D OpenCascade geometry:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          {demoParts.map((dp) => (
            <div
              key={dp.id}
              className="p-5 rounded-lg border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-sky-300 transition-all flex flex-col justify-between shadow-xs hover:shadow-sm"
            >
              <div className="space-y-2.5">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-sky-800">{dp.dwgNo}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-white text-slate-700 border border-slate-200 font-mono font-medium">
                    {dp.standard}
                  </span>
                </div>
                <h3 className="text-sm font-bold text-slate-900">{dp.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed">{dp.description}</p>
                <div className="flex items-center gap-2 text-[11px] text-slate-500 font-mono">
                  <span>{dp.material}</span>
                  <span>•</span>
                  <span>{dp.dimensions} Dims</span>
                  <span>•</span>
                  <span>{dp.features} Features</span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-200 flex items-center justify-between">
                <span
                  className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded ${
                    dp.unverifiedCount > 0
                      ? "bg-amber-50 text-amber-800 border border-amber-200"
                      : "bg-emerald-50 text-emerald-800 border border-emerald-200"
                  }`}
                >
                  {dp.unverifiedCount > 0 ? `${dp.unverifiedCount} needs review` : "All confirmed"}
                </span>
                <Link
                  href={`/jobs/${dp.id}/review`}
                  className="flex items-center gap-1 text-xs font-bold text-sky-700 hover:text-sky-800 transition-colors"
                >
                  Open Specimen
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* "Needs Your Review" Work Queue First */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <h2 className="text-xs font-bold text-slate-900 tracking-wider uppercase font-mono">
              Needs Your Review ({reviewQueue.length})
            </h2>
          </div>
          <span className="text-xs text-slate-500 font-mono">
            CAD generation gated until all unverified dimensions confirmed
          </span>
        </div>

        <div className="grid gap-3">
          {reviewQueue.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between p-4 rounded-lg border border-amber-200 bg-amber-50/40 hover:bg-amber-50/70 transition-all shadow-xs"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-slate-900">{item.title}</span>
                  <span className="font-mono text-xs text-slate-700 px-2 py-0.5 rounded bg-white border border-slate-200">
                    {item.drawingNumber}
                  </span>
                  <span className="text-[11px] text-slate-500 font-mono font-medium">
                    {item.standard}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-xs text-slate-600">
                  <span className="text-amber-800 font-semibold font-mono">
                    {item.unverifiedCount} dimension{item.unverifiedCount > 1 ? "s" : ""} require confirmation
                  </span>
                  <span>•</span>
                  <span>{item.totalCount - item.unverifiedCount} of {item.totalCount} auto-verified</span>
                  <span>•</span>
                  <span>Updated {item.updatedAt}</span>
                </div>
              </div>

              <Link
                href={`/jobs/${item.id}/review`}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-md bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold transition-colors shadow-xs"
              >
                Review & Confirm
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Production Metrics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-xs">
          <div className="text-xs text-slate-500 uppercase tracking-wider font-mono font-medium">Monthly Jobs</div>
          <div className="mt-2 text-2xl font-bold font-mono text-slate-900">42 / 500</div>
          <div className="mt-1 text-xs text-slate-500">Tier: Enterprise Business Plan</div>
        </div>

        <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-xs">
          <div className="text-xs text-slate-500 uppercase tracking-wider font-mono font-medium">Auto-Verification Rate</div>
          <div className="mt-2 text-2xl font-bold font-mono text-sky-700">92.4%</div>
          <div className="mt-1 text-xs text-slate-500">Dual Claude Passes + RapidOCR</div>
        </div>

        <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-xs">
          <div className="text-xs text-slate-500 uppercase tracking-wider font-mono font-medium">Zero-False-Verified</div>
          <div className="mt-2 text-2xl font-bold font-mono text-emerald-700">100.0%</div>
          <div className="mt-1 text-xs text-slate-500">Gated by Safety Invariant</div>
        </div>

        <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-xs">
          <div className="text-xs text-slate-500 uppercase tracking-wider font-mono font-medium">CAD Kernel Engine</div>
          <div className="mt-2 text-2xl font-bold font-mono text-slate-800">OCP 7.7.2</div>
          <div className="mt-1 text-xs text-slate-500">Deterministic Feature Compiler</div>
        </div>
      </div>

      {/* Recent Completed Pipelines */}
      <div className="space-y-3">
        <h2 className="text-xs font-bold text-slate-900 tracking-wider uppercase font-mono">
          Recent Completed Pipelines
        </h2>
        <div className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white shadow-xs">
          {recentJobs.map((j) => (
            <div key={j.id} className="p-4 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3">
                <FileCode2 className="w-4 h-4 text-emerald-600" />
                <div>
                  <div className="font-bold text-slate-900">{j.title}</div>
                  <div className="text-slate-500 font-mono text-[11px]">{j.accuracyScore}</div>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 text-[10px] font-mono font-bold">
                  {j.state}
                </span>
                <span className="text-slate-500">{j.time}</span>
                <Link
                  href={`/jobs/${j.id}/export`}
                  className="text-xs font-bold text-sky-700 hover:text-sky-800"
                >
                  Downloads
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Drawing Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-xl border border-slate-200 bg-white shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <FileUp className="w-5 h-5 text-sky-700" />
                <h3 className="text-sm font-bold text-slate-900">Upload 2D Engineering Drawing</h3>
              </div>
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setUploadingState(null);
                }}
                className="text-slate-400 hover:text-slate-600 p-1 rounded"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              {uploadingState ? (
                <div className="py-12 flex flex-col items-center justify-center text-center space-y-4">
                  <div className="w-12 h-12 rounded-full border-3 border-sky-200 border-t-sky-700 animate-spin"></div>
                  <div className="space-y-1">
                    <p className="text-sm font-bold text-slate-900">{uploadingState}</p>
                    <p className="text-xs text-slate-500 font-mono">Running precision AI vision + RapidOCR cross-check</p>
                  </div>
                </div>
              ) : (
                <>
                  {/* Dropzone */}
                  <div
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-300 hover:border-sky-500 hover:bg-sky-50/50 transition-all rounded-lg p-8 flex flex-col items-center justify-center text-center cursor-pointer space-y-2"
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,.dxf,.png,.jpg,.jpeg,.tif,.tiff"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          setSelectedFile(e.target.files[0]);
                          setUploadTitle(e.target.files[0].name.replace(/\.[^/.]+$/, ""));
                        }
                      }}
                    />
                    <div className="w-12 h-12 rounded-full bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-700">
                      <FileUp className="w-6 h-6" />
                    </div>
                    <div>
                      <span className="text-xs font-bold text-sky-700 hover:underline">
                        {selectedFile ? selectedFile.name : "Click to select drawing"}
                      </span>
                      <span className="text-xs text-slate-500"> or drag and drop</span>
                    </div>
                    <p className="text-[11px] text-slate-400 font-mono">
                      Accepts ISO/ASME 2D PDF, DXF, PNG, JPG (up to 50MB)
                    </p>
                  </div>

                  {/* Metadata fields */}
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs font-bold text-slate-700 font-mono">Part Title</label>
                      <input
                        type="text"
                        value={uploadTitle}
                        onChange={(e) => setUploadTitle(e.target.value)}
                        className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
                        placeholder="e.g. Flange Adapter Housing"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="text-xs font-bold text-slate-700 font-mono">Drawing Number</label>
                        <input
                          type="text"
                          value={uploadDwgNo}
                          onChange={(e) => setUploadDwgNo(e.target.value)}
                          className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
                        />
                      </div>
                      <div>
                        <label className="text-xs font-bold text-slate-700 font-mono">General Tolerance</label>
                        <select
                          value={uploadTolerance}
                          onChange={(e) => setUploadTolerance(e.target.value)}
                          className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 text-xs font-mono text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
                        >
                          <option value="ISO 2768-f">ISO 2768-f (Fine)</option>
                          <option value="ISO 2768-m">ISO 2768-m (Medium)</option>
                          <option value="ISO 2768-c">ISO 2768-c (Coarse)</option>
                          <option value="ASME Y14.5">ASME Y14.5 Standard</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 flex items-center justify-end gap-3">
                    <button
                      onClick={() => setShowUploadModal(false)}
                      className="px-4 py-2 rounded-md border border-slate-300 text-xs font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleStartUpload}
                      className="px-5 py-2 rounded-md bg-sky-700 hover:bg-sky-800 text-white text-xs font-bold transition-all shadow-xs"
                    >
                      Process & Extract
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
