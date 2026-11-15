import "./globals.css";
import React from "react";
import Link from "next/link";
import { Layers, ShieldCheck, Compass, Settings, Activity, Building2 } from "lucide-react";

export const metadata = {
  title: "Sketch2STEP Enterprise | 2D to 3D Parametric CAD Reconstruction",
  description: "Certified manufacturing CAD reconstruction guaranteeing every dimension is verified before STEP export.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased">
        {/* Precision Engineering Top Navigation Header */}
        <header className="h-14 border-b border-slate-200 bg-white px-6 flex items-center justify-between sticky top-0 z-50 shadow-xs">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-md bg-sky-50 border border-sky-200 flex items-center justify-center text-sky-700 group-hover:bg-sky-100 transition-colors shadow-xs">
                <Compass className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold tracking-tight text-slate-900">
                  Sketch2STEP
                </span>
                <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-300">
                  ENTERPRISE CAD
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-1 text-xs">
              <Link
                href="/"
                className="px-3 py-1.5 rounded-md font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors flex items-center gap-2"
              >
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                Pipeline Dashboard
              </Link>
              <Link
                href="/settings"
                className="px-3 py-1.5 rounded-md font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors flex items-center gap-2"
              >
                <Settings className="w-3.5 h-3.5 text-slate-500" />
                Settings & Standards
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-700">
              <Building2 className="w-3.5 h-3.5 text-sky-700" />
              <span className="font-mono text-[11px] text-slate-500">TENANT:</span>
              <span className="font-semibold text-slate-900">Alpha Precision Works</span>
              <span className="text-[10px] px-1 rounded bg-slate-200 text-slate-600 font-mono">ISO 9001</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-600 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 ring-2 ring-emerald-100 animate-pulse"></span>
              <span className="font-medium text-[11px]">System Ready</span>
            </div>
          </div>
        </header>

        {/* Main Workspace Body */}
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
