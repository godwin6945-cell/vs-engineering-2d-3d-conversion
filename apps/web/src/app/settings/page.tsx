"use client";

import React, { useState } from "react";
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
  Plus,
  Check,
  AlertCircle,
  Copy,
  Trash2
} from "lucide-react";

export default function SettingsPage() {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [byokKey, setByokKey] = useState("sk-ant-api03-••••••••••••••••••••••••");
  const [isEditingByok, setIsEditingByok] = useState(false);
  const [byokStatus, setByokStatus] = useState<string | null>(null);

  const [apiKeys, setApiKeys] = useState([
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
  ]);

  const [dimensionStandards, setDimensionStandards] = useState([
    { category: "thread", name: "M8x1.25 Standard Tap Drill", value: "6.8 mm", tol: "H7 (+0.015/-0)" },
    { category: "hole", name: "Dowel Pin Bore Ø10", value: "10.0 mm", tol: "+0.008/-0" },
    { category: "plate_thickness", name: "Standard Base Flange Stock", value: "16.0 mm", tol: "±0.1 mm" },
  ]);

  const [teamMembers, setTeamMembers] = useState([
    { name: "Alpha Owner", email: "owner@alpha.com", role: "OWNER", status: "Active" },
    { name: "John Doe", email: "lead.qa@alpha.com", role: "REVIEWER", status: "Active" },
    { name: "Rajesh Kumar", email: "cad.eng1@alpha.com", role: "ENGINEER", status: "Active" },
    { name: "Priya Sharma", email: "cad.eng2@alpha.com", role: "ENGINEER", status: "Active" },
  ]);

  const currentPlan = {
    tier: "Professional Enterprise",
    priceInr: "₹49,999",
    gstInr: "₹8,999.82",
    totalInr: "₹58,998.82",
    monthlyJobsLimit: 350,
    monthlyJobsUsed: 84,
    seatLimit: 10,
    seatsUsed: teamMembers.length,
    gstin: "29AABCU9603R1ZM",
    legalName: "Alpha Precision Works Pvt Ltd",
  };

  const handleCopy = (text: string) => {
    navigator.clipboard?.writeText(text);
    setCopiedKey(text);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const handleRevokeKey = (prefix: string) => {
    setApiKeys((prev) => prev.filter((k) => k.prefix !== prefix));
  };

  const handleGenerateKey = () => {
    const newPrefix = "sk2s_" + Math.random().toString(36).substring(2, 8);
    setApiKeys((prev) => [
      ...prev,
      {
        name: `Automated Pipeline Key #${prev.length + 1}`,
        prefix: newPrefix,
        created: new Date().toISOString().split("T")[0],
        lastUsed: "Just created",
      },
    ]);
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 text-slate-900 font-sans min-h-[calc(100vh-3.5rem)]">
      {/* Precision CAD Header Bar */}
      <div className="h-16 border-b border-slate-200 bg-white px-8 flex items-center justify-between shadow-xs">
        <div>
          <h1 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
            Enterprise Settings & Administration
          </h1>
          <p className="text-xs text-slate-500 font-mono">
            Tenant: <span className="font-semibold text-slate-800">Alpha Precision Works Pvt Ltd</span> • Org ID: alpha-precision
          </p>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-sky-50 border border-sky-200 text-xs font-mono text-sky-800 font-semibold">
          <Shield className="w-4 h-4 text-sky-600" />
          <span>SaaS Edition: Professional</span>
        </div>
      </div>

      <div className="flex-1 max-w-6xl mx-auto w-full p-8 space-y-6 overflow-y-auto">
        {/* 1. Subscription & Indian GST Billing */}
        <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-xs space-y-5">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-sky-50 border border-sky-200 text-sky-700">
                <CreditCard className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Subscription & Indian GST Billing
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  Razorpay Subscriptions • 18% GST (SAC 998314)
                </span>
              </div>
            </div>

            <span className="px-3 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-mono font-bold uppercase flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              Active Subscription
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1">
              <span className="text-[11px] text-slate-500 uppercase font-mono font-semibold">Current Plan</span>
              <div className="text-lg font-bold text-slate-900 font-mono">{currentPlan.tier}</div>
              <div className="text-xs text-slate-500 font-mono">
                {currentPlan.priceInr} / mo + 18% GST
              </div>
            </div>

            <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1">
              <span className="text-[11px] text-slate-500 uppercase font-mono font-semibold">Monthly Conversions</span>
              <div className="text-lg font-bold text-sky-700 font-mono">
                {currentPlan.monthlyJobsUsed} <span className="text-sm font-normal text-slate-500">/ {currentPlan.monthlyJobsLimit}</span>
              </div>
              <div className="text-xs text-slate-500 font-mono">
                Renews on 1st of next month
              </div>
            </div>

            <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1">
              <span className="text-[11px] text-slate-500 uppercase font-mono font-semibold">Tax Compliance (GSTIN)</span>
              <div className="text-sm font-bold text-emerald-700 font-mono">{currentPlan.gstin}</div>
              <div className="text-xs text-slate-600 truncate font-mono">
                {currentPlan.legalName}
              </div>
            </div>
          </div>
        </div>

        {/* 2. Security & BYOK Key */}
        <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-sky-50 border border-sky-200 text-sky-700">
                <Lock className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Bring Your Own Key (BYOK) & Extraction Security
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  Tenant-isolated envelope encryption (AES-256-GCM)
                </span>
              </div>
            </div>

            <span className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 border border-slate-300 text-xs font-mono font-medium">
              BYOK Enabled
            </span>
          </div>

          <p className="text-xs text-slate-600 leading-relaxed">
            Enterprise customers can supply their own Anthropic Claude 3.5 Sonnet API key to pay for extraction tokens directly. Your proprietary drawings are processed with zero data retention on AI inference servers.
          </p>

          <div className="flex gap-3">
            <input
              type="password"
              placeholder="sk-ant-api03-••••••••••••••••••••••••"
              disabled={!isEditingByok}
              value={byokKey}
              onChange={(e) => setByokKey(e.target.value)}
              className="flex-1 px-3 py-2 rounded-md bg-slate-50 border border-slate-300 text-xs font-mono text-slate-800 disabled:bg-slate-100"
            />
            {isEditingByok ? (
              <button
                onClick={() => {
                  setIsEditingByok(false);
                  setByokStatus("Key saved successfully");
                  setTimeout(() => setByokStatus(null), 3000);
                }}
                className="px-4 py-2 rounded-md bg-sky-700 hover:bg-sky-800 text-white font-mono text-xs font-bold transition-colors shadow-xs"
              >
                Save Key
              </button>
            ) : (
              <button
                onClick={() => setIsEditingByok(true)}
                className="px-4 py-2 rounded-md bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 font-mono text-xs font-bold transition-colors"
              >
                Update Key
              </button>
            )}
          </div>
          {byokStatus && (
            <div className="text-xs text-emerald-700 font-mono flex items-center gap-1.5">
              <Check className="w-3.5 h-3.5" /> {byokStatus}
            </div>
          )}
        </div>

        {/* 3. Programmatic API Keys (ERP/PLM) */}
        <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-sky-50 border border-sky-200 text-sky-700">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Programmatic REST API Keys
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  For automated pipeline triggering via Siemens Teamcenter, PTC Windchill, or SAP ERP
                </span>
              </div>
            </div>

            <button
              onClick={handleGenerateKey}
              className="px-3.5 py-1.5 rounded-md bg-sky-700 hover:bg-sky-800 text-white font-mono text-xs font-bold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              Generate API Key
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {apiKeys.map((k) => (
              <div key={k.prefix} className="py-3 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-bold text-slate-900">{k.name}</div>
                  <div className="text-[11px] text-slate-500">Key: <span className="text-slate-700">{k.prefix}••••••••••••</span> • Created {k.created}</div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right text-slate-500 text-[11px]">
                    Last used: {k.lastUsed}
                  </div>
                  <button
                    onClick={() => handleCopy(k.prefix)}
                    className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                    title="Copy Key Prefix"
                  >
                    {copiedKey === k.prefix ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                  <button
                    onClick={() => handleRevokeKey(k.prefix)}
                    className="text-red-600 hover:text-red-700 hover:underline text-[11px] font-semibold"
                  >
                    Revoke
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 4. Dimension Library (Recurring Standards) */}
        <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-sky-50 border border-sky-200 text-sky-700">
                <Sliders className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Company Dimension Library & Tolerances
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  Recurring shop tolerances and standard feature templates (ISO 2768-m)
                </span>
              </div>
            </div>

            <button
              onClick={() => {
                const name = prompt("Enter feature standard name (e.g., M10 Tap Hole):");
                if (name) {
                  setDimensionStandards((prev) => [
                    ...prev,
                    { category: "hole", name, value: "8.5 mm", tol: "±0.05 mm" },
                  ]);
                }
              }}
              className="px-3.5 py-1.5 rounded-md bg-sky-700 hover:bg-sky-800 text-white font-mono text-xs font-bold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              Add Dimension Standard
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {dimensionStandards.map((std) => (
              <div key={std.name} className="py-3 flex items-center justify-between text-xs font-mono">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700 border border-slate-200">
                    {std.category}
                  </span>
                  <span className="font-bold text-slate-900">{std.name}</span>
                </div>
                <div className="text-slate-800 font-bold bg-slate-50 px-2.5 py-1 rounded border border-slate-200">
                  {std.value} <span className="text-slate-500 font-normal">({std.tol})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 5. Team Seats & Roles */}
        <div className="p-6 rounded-lg bg-white border border-slate-200 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-200">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-md bg-sky-50 border border-sky-200 text-sky-700">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Team Members & Roles ({teamMembers.length} of {currentPlan.seatLimit} seats)
                </h2>
                <span className="text-xs text-slate-500 font-mono">
                  Role-based access control (Owner, Admin, Reviewer, Engineer, Viewer)
                </span>
              </div>
            </div>

            <button
              onClick={() => {
                const email = prompt("Enter team member work email:");
                if (email) {
                  setTeamMembers((prev) => [
                    ...prev,
                    { name: email.split("@")[0], email, role: "ENGINEER", status: "Active" },
                  ]);
                }
              }}
              className="px-3.5 py-1.5 rounded-md bg-sky-700 hover:bg-sky-800 text-white font-mono text-xs font-bold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              <Plus className="w-3.5 h-3.5" />
              Invite Member
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {teamMembers.map((m) => (
              <div key={m.email} className="py-3 flex items-center justify-between text-xs font-mono">
                <div>
                  <div className="font-bold text-slate-900">{m.name}</div>
                  <div className="text-[11px] text-slate-500">{m.email}</div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="px-2 py-0.5 rounded-md bg-sky-50 text-sky-800 border border-sky-200 text-[10px] font-bold">
                    {m.role}
                  </span>
                  <span className="text-emerald-700 font-semibold text-[10px] flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                    {m.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
