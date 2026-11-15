import React from "react";
import {
  Building2,
  CreditCard,
  KeyRound,
  Layers,
  Lock,
  Receipt,
  Shield,
  Sliders,
  Users,
  Webhook,
  FileCheck2,
} from "lucide-react";

export default function SettingsPage() {
  const currentPlan = {
    tier: "Professional",
    priceInr: "₹49,999",
    gstInr: "₹8,999.82",
    totalInr: "₹58,998.82",
    monthlyJobsLimit: 350,
    monthlyJobsUsed: 84,
    seatLimit: 10,
    seatsUsed: 4,
    gstin: "29AABCU9603R1ZM",
    legalName: "Alpha Precision Works Pvt Ltd",
  };

  const teamMembers = [
    { name: "Alpha Owner", email: "owner@alpha.com", role: "OWNER", status: "Active" },
    { name: "John Doe", email: "lead.qa@alpha.com", role: "REVIEWER", status: "Active" },
    { name: "Rajesh Kumar", email: "cad.eng1@alpha.com", role: "ENGINEER", status: "Active" },
    { name: "Priya Sharma", email: "cad.eng2@alpha.com", role: "ENGINEER", status: "Active" },
  ];

  const apiKeys = [
    {
      name: "Siemens Teamcenter PLM Sync",
      prefix: "sk2s_tc8912",
      created: "2026-10-12",
      lastUsed: "2 hours ago",
    },
    {
      name: "SAP ERP Production Batch",
      prefix: "sk2s_sap441",
      created: "2026-11-01",
      lastUsed: "Yesterday",
    },
  ];

  const dimensionStandards = [
    { category: "thread", name: "M8x1.25 Standard Tap Drill", value: "6.8 mm", tol: "H7 (+0.015/-0)" },
    { category: "hole", name: "Dowel Pin Bore Ø10", value: "10.0 mm", tol: "+0.008/-0" },
    { category: "plate_thickness", name: "Standard Base Flange Stock", value: "16.0 mm", tol: "±0.1 mm" },
  ];

  return (
    <div className="flex-1 flex flex-col bg-[#090d12] text-slate-100 font-sans min-h-[calc(100vh-3.5rem)]">
      {/* Header Bar */}
      <div className="h-16 border-b border-[#222f3e] bg-[#111720] px-8 flex items-center justify-between">
        <div>
          <h1 className="text-base font-bold text-white tracking-wide">
            Enterprise Settings & Administration
          </h1>
          <p className="text-xs text-slate-400 font-mono">
            Tenant: Alpha Precision Works Pvt Ltd • Org ID: alpha-precision
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
          <Shield className="w-3.5 h-3.5 text-cyan-400" />
          <span>SaaS Edition: Professional</span>
        </div>
      </div>

      <div className="flex-1 max-w-6xl mx-auto w-full p-8 space-y-8 overflow-y-auto">
        {/* 1. Subscription & Indian GST Billing */}
        <div className="p-6 rounded-lg bg-[#111720] border border-[#222f3e] space-y-5 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
            <div className="flex items-center gap-2.5">
              <CreditCard className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Subscription & Indian GST Billing
                </h2>
                <span className="text-[11px] text-slate-400 font-mono">
                  Razorpay Subscriptions • 18% GST (SAC 998314)
                </span>
              </div>
            </div>

            <span className="px-3 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-xs font-mono font-bold uppercase">
              Active Subscription
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded bg-[#0b1017] border border-[#1e293b] space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-mono">Current Plan</span>
              <div className="text-lg font-bold text-white font-mono">{currentPlan.tier}</div>
              <div className="text-xs text-slate-400 font-mono">
                {currentPlan.priceInr} / month + 18% GST
              </div>
            </div>

            <div className="p-4 rounded bg-[#0b1017] border border-[#1e293b] space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-mono">Drawing Conversions</span>
              <div className="text-lg font-bold text-cyan-300 font-mono">
                {currentPlan.monthlyJobsUsed} / {currentPlan.monthlyJobsLimit}
              </div>
              <div className="text-xs text-slate-400 font-mono">
                Renews on 1st of next month
              </div>
            </div>

            <div className="p-4 rounded bg-[#0b1017] border border-[#1e293b] space-y-1">
              <span className="text-[10px] text-slate-400 uppercase font-mono">Tax Compliance (GSTIN)</span>
              <div className="text-sm font-bold text-emerald-400 font-mono">{currentPlan.gstin}</div>
              <div className="text-xs text-slate-400 truncate font-mono">
                {currentPlan.legalName}
              </div>
            </div>
          </div>
        </div>

        {/* 2. Security & BYOK Key */}
        <div className="p-6 rounded-lg bg-[#111720] border border-[#222f3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
            <div className="flex items-center gap-2.5">
              <Lock className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Bring Your Own Key (BYOK) & Security
                </h2>
                <span className="text-[11px] text-slate-400 font-mono">
                  Envelope-encrypted storage (AES-256-GCM) with tenant-isolated KMS key
                </span>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded bg-slate-800 text-slate-300 border border-slate-700 text-xs font-mono">
              BYOK Enabled
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Enterprise customers can supply their own Anthropic API key to pay for Claude Opus extraction tokens directly. Your proprietary 2D drawings are processed without zero data retention on AI provider servers.
          </p>

          <div className="flex gap-3">
            <input
              type="password"
              placeholder="sk-ant-api03-••••••••••••••••••••••••"
              disabled
              value="sk-ant-api03-example-configured-key"
              className="flex-1 px-3 py-2 rounded bg-[#0b1017] border border-[#222f3e] text-xs font-mono text-slate-300"
            />
            <button className="px-4 py-2 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold transition-colors">
              Update Key
            </button>
          </div>
        </div>

        {/* 3. Programmatic API Keys (ERP/PLM) */}
        <div className="p-6 rounded-lg bg-[#111720] border border-[#222f3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
            <div className="flex items-center gap-2.5">
              <KeyRound className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Programmatic REST API Keys
                </h2>
                <span className="text-[11px] text-slate-400 font-mono">
                  For automated pipeline triggering via Siemens Teamcenter, Windchill, or SAP
                </span>
              </div>
            </div>

            <button className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold transition-colors">
              + Generate New API Key
            </button>
          </div>

          <div className="divide-y divide-[#1e293b]">
            {apiKeys.map((k) => (
              <div key={k.prefix} className="py-3 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-bold text-white">{k.name}</div>
                  <div className="text-[11px] text-slate-400">Prefix: {k.prefix}••••</div>
                </div>
                <div className="text-right text-slate-400 text-[11px]">
                  <div>Last used: {k.lastUsed}</div>
                  <button className="text-red-400 hover:underline text-[10px]">Revoke</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Dimension Library (Recurring Standards) */}
        <div className="p-6 rounded-lg bg-[#111720] border border-[#222f3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
            <div className="flex items-center gap-2.5">
              <Sliders className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Company Dimension Library
                </h2>
                <span className="text-[11px] text-slate-400 font-mono">
                  Recurring shop tolerances and standard feature templates
                </span>
              </div>
            </div>

            <button className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold transition-colors">
              + Add Dimension Standard
            </button>
          </div>

          <div className="divide-y divide-[#1e293b]">
            {dimensionStandards.map((std) => (
              <div key={std.name} className="py-3 flex items-center justify-between text-xs font-mono">
                <div>
                  <span className="px-1.5 py-0.5 rounded text-[9px] uppercase font-bold bg-slate-800 text-slate-300 mr-2">
                    {std.category}
                  </span>
                  <span className="font-bold text-white">{std.name}</span>
                </div>
                <div className="text-slate-300 font-bold">
                  {std.value} ({std.tol})
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 5. Team Seats & Roles */}
        <div className="p-6 rounded-lg bg-[#111720] border border-[#222f3e] space-y-4 shadow-lg">
          <div className="flex items-center justify-between pb-3 border-b border-[#222f3e]">
            <div className="flex items-center gap-2.5">
              <Users className="w-5 h-5 text-cyan-400" />
              <div>
                <h2 className="text-sm font-bold text-white uppercase tracking-wider">
                  Team Members & Roles ({teamMembers.length} of {currentPlan.seatLimit} seats)
                </h2>
                <span className="text-[11px] text-slate-400 font-mono">
                  Role-based access control (Owner, Admin, Engineer, Reviewer, Viewer)
                </span>
              </div>
            </div>

            <button className="px-3 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-mono text-xs font-bold transition-colors">
              + Invite Member
            </button>
          </div>

          <div className="divide-y divide-[#1e293b]">
            {teamMembers.map((m) => (
              <div key={m.email} className="py-3 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-bold text-white">{m.name}</div>
                  <div className="text-[11px] text-slate-400">{m.email}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700 text-[10px] font-bold">
                    {m.role}
                  </span>
                  <span className="text-emerald-400 text-[10px]">{m.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
