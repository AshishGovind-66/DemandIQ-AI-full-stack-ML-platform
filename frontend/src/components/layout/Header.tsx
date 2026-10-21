"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Activity, Database, CheckCircle2, AlertCircle } from "lucide-react";

export function Header({ title }: { title?: string }) {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [version, setVersion] = useState<string>("1.0.0");

  useEffect(() => {
    api
      .getHealth()
      .then((res) => {
        setIsHealthy(res.status === "healthy");
        setVersion(res.version);
      })
      .catch(() => setIsHealthy(false));
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h2 className="text-lg font-semibold text-slate-900">{title || "DemandIQ AI"}</h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Backend Connectivity Status Pill */}
        <div className="flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200">
          <span className="text-slate-500">API Backend:</span>
          {isHealthy === true && (
            <span className="flex items-center text-emerald-600 font-semibold space-x-1">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Online (v{version})</span>
            </span>
          )}
          {isHealthy === false && (
            <span className="flex items-center text-amber-600 font-semibold space-x-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Offline / Starting</span>
            </span>
          )}
          {isHealthy === null && <span className="text-slate-400">Connecting...</span>}
        </div>
      </div>
    </header>
  );
}

