import "./globals.css";
import React from "react";
import Link from "next/link";
import { Layers, ShieldCheck, Compass, Settings, Activity } from "lucide-react";

export const metadata = {
  title: "Sketch2STEP Enterprise | Precision 2D to 3D Conversion",
  description: "Enterprise CAD reconstruction guaranteeing every dimension is verified before STEP export.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen flex flex-col bg-[#090d12] text-slate-100">
        {/* Precision Engineering Top Navigation Bar */}
        <header className="h-14 border-b border-[#222f3e] bg-[#111720] px-6 flex items-center justify-between sticky top-0 z-50">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2.5 font-semibold tracking-tight text-white">
              <div className="w-7 h-7 rounded bg-cyan-600/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
                <Compass className="w-4 h-4" />
              </div>
              <span className="text-sm font-semibold tracking-wider uppercase">Sketch2STEP</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800 font-mono">ENTERPRISE</span>
            </Link>

            <nav className="hidden md:flex items-center gap-1 text-xs">
              <Link
                href="/"
                className="px-3 py-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <Layers className="w-3.5 h-3.5 text-slate-400" />
                Pipeline Dashboard
              </Link>
              <Link
                href="/settings"
                className="px-3 py-1.5 rounded text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <Settings className="w-3.5 h-3.5 text-slate-400" />
                Settings & BYOK
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-slate-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-mono text-[11px] text-slate-400">TENANT:</span>
              <span className="font-medium text-slate-200">Alpha Precision Works</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Activity className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px]">System Ready</span>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 flex flex-col">{children}</main>
      </body>
    </html>
  );
}
