"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, DataProfilingReport } from "@/types";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";
import {
  BarChart2,
  Calendar,
  Layers,
  Percent,
  TrendingUp,
  AlertCircle,
  FileSpreadsheet
} from "lucide-react";

export default function EDAPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [profile, setProfile] = useState<DataProfilingReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) {
        setSelectedDatasetId(list[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) return;
    setLoading(true);
    setError(null);
    api
      .getDatasetProfile(selectedDatasetId)
      .then((rep) => {
        setProfile(rep);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load exploratory analysis.");
        setLoading(false);
      });
  }, [selectedDatasetId]);

  return (
    <AppShell title="Exploratory Data Analysis (EDA)">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Top Control Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Sales Pattern Analysis</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Empirical demand distributions, seasonality, day-of-week trends, and product rankings.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-semibold text-slate-600">Active Dataset:</span>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600" />
            <span>{error}</span>
          </div>
        )}

        {loading ? (
          <div className="py-20 text-center text-slate-400 font-medium">Computing empirical data distributions...</div>
        ) : profile ? (
          <div className="space-y-6">
            {/* Statistical KPI Row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Total Sales</span>
                <div className="text-xl font-bold text-slate-900 mt-1">{profile.total_sales_volume.toLocaleString()}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{profile.total_duration_days} days logged</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Mean Daily Sales</span>
                <div className="text-xl font-bold text-slate-900 mt-1">{profile.mean_daily_sales.toFixed(1)}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Median: {profile.median_daily_sales}</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Std Deviation (σ)</span>
                <div className="text-xl font-bold text-slate-900 mt-1">{profile.std_daily_sales.toFixed(1)}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Demand volatility</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Zero Sales %</span>
                <div className="text-xl font-bold text-slate-900 mt-1">{profile.zero_sales_percentage}%</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Intermittent ratio</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Unique SKUs</span>
                <div className="text-xl font-bold text-slate-900 mt-1">{profile.unique_products_count}</div>
                <div className="text-[11px] text-slate-400 mt-0.5">{profile.unique_stores_count} stores</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold text-slate-500 uppercase">Date Range</span>
                <div className="text-xs font-bold text-slate-800 mt-2 truncate">{profile.start_date}</div>
                <div className="text-xs text-slate-500 truncate">to {profile.end_date}</div>
              </div>
            </div>

            {/* Daily Trend Chart */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-900 text-base">Historical Demand Trajectory</h3>
                <span className="text-xs text-slate-400">Sample of actual sales aggregated over time</span>
              </div>
              <div className="h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={profile.daily_trend_sample}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickMargin={8} />
                    <YAxis stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", color: "#fff", border: "none" }}
                    />
                    <Line type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Two Column Layout for Seasonality & Top Products */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Day of Week Seasonality */}
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-slate-900 text-base">Weekly Seasonality Profile</h3>
                  <span className="text-xs text-slate-400">Average sales per day of week</span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={profile.day_of_week_pattern}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="day" stroke="#94a3b8" fontSize={12} />
                      <YAxis stroke="#94a3b8" fontSize={11} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", color: "#fff", border: "none" }}
                      />
                      <Bar dataKey="avg_sales" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Top Selling Products */}
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-bold text-slate-900 text-base">Top Selling Products</h3>
                  <span className="text-xs text-slate-400">Total historical sales</span>
                </div>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={profile.top_products.slice(0, 8)} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                      <YAxis type="category" dataKey="product_id" stroke="#94a3b8" fontSize={11} width={90} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", color: "#fff", border: "none" }}
                      />
                      <Bar dataKey="total_sales" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}

