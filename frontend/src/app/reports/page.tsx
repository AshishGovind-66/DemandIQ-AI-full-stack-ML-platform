"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import {
  FileSpreadsheet,
  Download,
  FileCode,
  Calendar,
  CheckCircle2,
  HardDrive
} from "lucide-react";

export default function ReportsPage() {
  const [reports, setReports] = useState<Array<{
    filename: string;
    size_bytes: number;
    modified_time: number;
    type: string;
    download_url: string;
  }>>([]);
  const [loading, setLoading] = useState(true);

  const fetchReports = () => {
    setLoading(true);
    api
      .getReports()
      .then((res) => {
        setReports(res.reports || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  return (
    <AppShell title="Reports, Exports & Analytics Artifacts">
      <div className="space-y-6 max-w-7xl mx-auto">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Exported Analytical Reports</h1>
          <p className="text-xs text-slate-500 mt-1">
            Download generated CSV forecast series, inventory replenishment recommendations, and profiling summaries.
          </p>
        </div>

        {/* Report List */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-400">Loading export archives...</div>
          ) : reports.length > 0 ? (
            <div className="divide-y divide-slate-100">
              {reports.map((rep) => (
                <div key={rep.filename} className="p-4 flex items-center justify-between hover:bg-slate-50">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                      {rep.type === "CSV" ? <FileSpreadsheet className="w-5 h-5" /> : <FileCode className="w-5 h-5" />}
                    </div>
                    <div>
                      <div className="font-bold text-sm text-slate-900">{rep.filename}</div>
                      <div className="text-xs text-slate-400 flex items-center space-x-3 mt-0.5">
                        <span>{(rep.size_bytes / 1024).toFixed(1)} KB</span>
                        <span>&bull;</span>
                        <span>{new Date(rep.modified_time * 1000).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <a
                    href={`${API_BASE}${rep.download_url}`}
                    download
                    className="inline-flex items-center space-x-1.5 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-900 hover:bg-slate-800 text-white transition-colors shadow-sm"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download {rep.type}</span>
                  </a>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-sm text-slate-500">
              No export files found. Generate a forecast or inventory plan to export results.
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

