"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { MetricCard } from "@/components/ui/MetricCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { api } from "@/lib/api";
import { DashboardSummary } from "@/types";
import {
  Package,
  TrendingUp,
  AlertTriangle,
  Archive,
  Trophy,
  History,
  ArrowRight,
  Database,
  Cpu,
  RefreshCw
} from "lucide-react";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    api
      .getDashboardSummary()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load dashboard metrics.");
        setLoading(false);
      });
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <AppShell title="Executive Overview Dashboard">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Top Header & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Demand &amp; Inventory Overview</h1>
            <p className="text-sm text-slate-500 mt-1">
              Live operational metrics derived directly from trained models and inventory policies.
            </p>
          </div>
          <button
            onClick={loadData}
            disabled={loading}
            className="inline-flex items-center space-x-2 px-3.5 py-2 text-sm font-medium rounded-lg border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 shadow-sm transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-600" : "text-slate-500"}`} />
            <span>Refresh</span>
          </button>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm">
            <span className="font-semibold">Notice:</span> {error} (Ensure backend server is running on port 8000)
          </div>
        )}

        {/* High Level KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <MetricCard
            title="Tracked Products"
            value={loading ? "..." : (data?.total_products ?? 0)}
            subtitle="Across active catalogs"
            icon={Package}
          />
          <MetricCard
            title="Historical Sales"
            value={loading ? "..." : (data?.total_historical_sales ? `${data.total_historical_sales.toLocaleString()} units` : "0 units")}
            subtitle="Verified historical volume"
            icon={History}
          />
          <MetricCard
            title="Forecasted Demand"
            value={
              loading
                ? "..."
                : data?.latest_forecast.has_forecast
                ? `${data.latest_forecast.total_demand.toLocaleString()} units`
                : "No run"
            }
            subtitle={
              data?.latest_forecast.has_forecast
                ? `${data.latest_forecast.horizon_days}d (${data.latest_forecast.model_name})`
                : "Run forecast under Forecasts"
            }
            icon={TrendingUp}
          />
          <MetricCard
            title="Stockout Risks"
            value={loading ? "..." : (data?.latest_inventory.stockout_risk_count ?? 0)}
            subtitle="Items where stock ≤ ROP"
            icon={AlertTriangle}
            trend={data?.latest_inventory.stockout_risk_count ? "Action needed" : "Healthy"}
            trendPositive={!data?.latest_inventory.stockout_risk_count}
          />
          <MetricCard
            title="Excess Stock"
            value={loading ? "..." : (data?.latest_inventory.excess_stock_count ?? 0)}
            subtitle="Cover > 60 days"
            icon={Archive}
          />
        </div>

        {/* Model Performance & Recent Workflows Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Best Model Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Best Performing Model
                </span>
                <div className="w-8 h-8 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
                  <Trophy className="w-4 h-4" />
                </div>
              </div>

              {data?.best_model ? (
                <div className="mt-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-xl font-bold text-slate-900 uppercase">
                      {data.best_model.model_name.replace("_", " ")}
                    </span>
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
                      LEADER
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-slate-500 font-medium">WAPE Error</div>
                      <div className="text-base font-bold text-slate-800">
                        {data.best_model.metrics ? `${(data.best_model.metrics.wape * 100).toFixed(1)}%` : "N/A"}
                      </div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-slate-500 font-medium">MAE</div>
                      <div className="text-base font-bold text-slate-800">
                        {data.best_model.metrics ? data.best_model.metrics.mae.toFixed(2) : "N/A"}
                      </div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-slate-500 font-medium">RMSE</div>
                      <div className="text-base font-bold text-slate-800">
                        {data.best_model.metrics ? data.best_model.metrics.rmse.toFixed(2) : "N/A"}
                      </div>
                    </div>
                    <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                      <div className="text-xs text-slate-500 font-medium">Forecast Bias</div>
                      <div className="text-base font-bold text-slate-800">
                        {data.best_model.metrics ? `${(data.best_model.metrics.bias * 100).toFixed(1)}%` : "N/A"}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="mt-6 text-sm text-slate-500">
                  No models trained yet. Initiate model training to generate validation metrics.
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100">
              <Link
                href="/models"
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center"
              >
                <span>View Full Model Leaderboard</span>
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </div>
          </div>

          {/* Recent Training Jobs */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Recent Model Training Workflows
                </span>
                <Link
                  href="/training"
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700 inline-flex items-center"
                >
                  <span>New Training Run</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Link>
              </div>

              {data?.recent_jobs && data.recent_jobs.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {data.recent_jobs.map((job) => (
                    <div key={job.id} className="py-3 flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                          <Cpu className="w-4 h-4" />
                        </div>
                        <div>
                          <div className="font-medium text-slate-800">
                            Training: {job.models_to_train.join(", ")}
                          </div>
                          <div className="text-xs text-slate-400 mt-0.5">{job.current_step}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <StatusBadge status={job.status} />
                        <span className="text-xs text-slate-400">
                          {job.created_at ? new Date(job.created_at).toLocaleTimeString() : ""}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="py-8 text-center text-sm text-slate-500">
                  No training jobs logged yet. Head to Model Training to evaluate models.
                </div>
              )}
            </div>

            {/* Quick Navigation Footer */}
            <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap items-center gap-3">
              <Link
                href="/datasets"
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
              >
                1. Inspect Datasets
              </Link>
              <Link
                href="/training"
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
              >
                2. Train Models
              </Link>
              <Link
                href="/forecasts"
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
              >
                3. Forecast Demand
              </Link>
              <Link
                href="/inventory"
                className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium transition-colors"
              >
                4. Optimize Inventory
              </Link>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

