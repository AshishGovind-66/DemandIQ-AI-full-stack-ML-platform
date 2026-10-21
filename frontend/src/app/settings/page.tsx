"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { HealthResponse } from "@/types";
import {
  Settings,
  Server,
  Database,
  CheckCircle2,
  AlertTriangle,
  Cpu,
  Layers,
  Sparkles,
  RefreshCw
} from "lucide-react";

export default function SettingsPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = () => {
    setLoading(true);
    api
      .getHealth()
      .then((res) => {
        setHealth(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <AppShell title="System Settings & Diagnostics">
      <div className="space-y-6 max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">System Architecture &amp; Environment</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Local runtime health, database connection, Walmart M5 dataset discovery, and registered ML algorithms.
            </p>
          </div>

          <button
            onClick={fetchHealth}
            disabled={loading}
            className="inline-flex items-center space-x-2 px-3.5 py-2 text-xs font-semibold rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            <span>Check Connectivity</span>
          </button>
        </div>

        {health ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Backend Runtime Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
                <Server className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-base">Backend &amp; Environment</h3>
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500">Service Status</span>
                  <span className="font-semibold text-emerald-600 flex items-center space-x-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Operational ({health.status})</span>
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500">Engine Version</span>
                  <span className="font-mono font-bold text-slate-800">v{health.version}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500">Environment Mode</span>
                  <span className="uppercase font-semibold text-slate-800">{health.environment}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500">Database Engine</span>
                  <span className="font-bold text-slate-800 uppercase">{health.database}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-slate-100">
                  <span className="text-slate-500">Python Runtime</span>
                  <span className="font-mono text-slate-800">{health.system_info.python_version}</span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-slate-500">Host OS</span>
                  <span className="text-slate-800 truncate max-w-[200px]">{health.system_info.platform}</span>
                </div>
              </div>
            </div>

            {/* Walmart M5 Dataset Discovery Card */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center space-x-2">
                  <Database className="w-5 h-5 text-blue-600" />
                  <h3 className="font-bold text-slate-900 text-base">Walmart M5 Dataset Files</h3>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    health.walmart_m5_available
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {health.walmart_m5_available ? "CORE PRESENT" : "PARTIAL / ABSENT"}
                </span>
              </div>

              <div className="space-y-2 text-xs">
                {Object.entries(health.system_info.m5_files || {}).map(([fname, fInfo]: any) => (
                  <div key={fname} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between">
                    <div>
                      <div className="font-bold text-slate-800">{fname}</div>
                      <div className="text-[11px] text-slate-400 mt-0.5 truncate max-w-[240px]">
                        {fInfo.path || "Not detected in data/raw or root"}
                      </div>
                    </div>
                    <div className="text-right">
                      {fInfo.available ? (
                        <span className="text-emerald-600 font-semibold">{fInfo.size_mb} MB</span>
                      ) : (
                        <span className="text-slate-400">Missing</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Registered ML Models Card */}
            <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
              <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
                <Cpu className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-base">Active Registered ML Forecasters</h3>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 pt-2">
                {health.available_models.map((modKey) => (
                  <div key={modKey} className="p-3 rounded-lg border border-slate-200 bg-slate-50 text-center">
                    <div className="font-bold text-xs text-slate-900 uppercase">{modKey.replace("_", " ")}</div>
                    <div className="text-[10px] text-emerald-600 font-semibold mt-1">Verified Ready</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="p-12 text-center text-sm text-slate-500">
            Cannot reach backend server. Please verify backend is running on port 8000.
          </div>
        )}
      </div>
    </AppShell>
  );
}

