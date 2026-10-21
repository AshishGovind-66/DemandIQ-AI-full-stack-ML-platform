"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Database,
  BarChart3,
  Cpu,
  Trophy,
  TrendingUp,
  PackageCheck,
  BrainCircuit,
  FileSpreadsheet,
  Settings,
  Sparkles
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Datasets", href: "/datasets", icon: Database },
  { label: "Exploratory Analysis", href: "/eda", icon: BarChart3 },
  { label: "Model Training", href: "/training", icon: Cpu },
  { label: "Model Leaderboard", href: "/models", icon: Trophy },
  { label: "Demand Forecasts", href: "/forecasts", icon: TrendingUp },
  { label: "Inventory Optimization", href: "/inventory", icon: PackageCheck },
  { label: "Explainable AI (SHAP)", href: "/explainability", icon: BrainCircuit },
  { label: "Reports & Exports", href: "/reports", icon: FileSpreadsheet },
  { label: "System Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col min-h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <Sparkles className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-tight leading-none">DemandIQ AI</h1>
          <p className="text-xs text-slate-400 mt-1">Enterprise Forecast & Stock</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-blue-600 text-white shadow-sm shadow-blue-600/30"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-white" : "text-slate-400"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* System Footer Info */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-400">
        <div className="flex items-center justify-between">
          <span>Engine v1.0</span>
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            MLOps Ready
          </span>
        </div>
        <p className="mt-1 text-[11px] text-slate-500 truncate">Walmart M5 & Custom CSV</p>
      </div>
    </aside>
  );
}

