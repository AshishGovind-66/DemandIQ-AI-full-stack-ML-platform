"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, ForecastResponse } from "@/types";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";
import {
  TrendingUp,
  Download,
  Calendar,
  Layers,
  Sparkles,
  AlertCircle,
  Package
} from "lucide-react";

export default function ForecastsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [horizonDays, setHorizonDays] = useState<number>(14);
  const [confidenceLevel, setConfidenceLevel] = useState<number>(0.95);
  const [forecastResult, setForecastResult] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) setSelectedDatasetId(list[0].id);
    });
  }, []);

  const handleGenerateForecast = async () => {
    if (!selectedDatasetId) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.generateForecast({
        dataset_id: selectedDatasetId,
        horizon_days: horizonDays,
        confidence_level: confidenceLevel,
      });
      setForecastResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to generate forecast.");
    } finally {
      setLoading(false);
    }
  };

  // Combine historical and future forecast points for seamless Recharts line visualization
  const chartData: any[] = [];
  if (forecastResult) {
    if (forecastResult.historical_comparison) {
      forecastResult.historical_comparison.forEach((pt) => {
        chartData.push({
          date: pt.date,
          historical: pt.actual_sales,
          predicted: null,
          upper: null,
          lower: null,
        });
      });
    }

    // Group forecast points by date to aggregate for multi-product charts
    const dateMap: Record<string, { pred: number; low: number; up: number }> = {};
    forecastResult.forecast_points_sample.forEach((pt) => {
      if (!dateMap[pt.date]) {
        dateMap[pt.date] = { pred: 0, low: 0, up: 0 };
      }
      dateMap[pt.date].pred += pt.predicted_demand;
      dateMap[pt.date].low += pt.lower_bound;
      dateMap[pt.date].up += pt.upper_bound;
    });

    Object.entries(dateMap).forEach(([dStr, vals]) => {
      chartData.push({
        date: dStr,
        historical: null,
        predicted: Math.round(vals.pred * 10) / 10,
        upper: Math.round(vals.up * 10) / 10,
        lower: Math.round(vals.low * 10) / 10,
      });
    });
  }

  return (
    <AppShell title="Demand Forecasting Engine">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Controls Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Generate Demand Forecast</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Multi-step forward trajectory with expanding empirical prediction uncertainty intervals.
              </p>
            </div>

            <button
              onClick={handleGenerateForecast}
              disabled={loading || !selectedDatasetId}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all shadow-md shadow-blue-500/25 disabled:bg-slate-300"
            >
              <Sparkles className={`w-4 h-4 ${loading ? "animate-spin" : "fill-white"}`} />
              <span>{loading ? "Generating Forecast..." : "Generate Forecast"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-3 border-t border-slate-100">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Target Dataset</label>
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">Horizon Duration</label>
              <div className="flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
                {[7, 14, 30].map((days) => (
                  <button
                    key={days}
                    onClick={() => setHorizonDays(days)}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
                      horizonDays === days
                        ? "bg-white text-blue-600 shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    {days} Days
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5">Confidence Level</label>
              <div className="flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
                {[0.90, 0.95, 0.99].map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setConfidenceLevel(lvl)}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-md transition-all ${
                      confidenceLevel === lvl
                        ? "bg-white text-blue-600 shadow-sm"
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    {intPercentage(lvl)}%
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {forecastResult && (
          <div className="space-y-6">
            {/* KPI Summary Row */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Total Projected Demand</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {forecastResult.total_forecasted_demand.toLocaleString()} units
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Across {forecastResult.points_count} points</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Average Daily Demand</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  {forecastResult.average_daily_demand.toFixed(1)} units/day
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Expected velocity</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Forecasting Model</span>
                <div className="text-xl font-bold text-slate-900 mt-1 uppercase">
                  {forecastResult.model_name.replace("_", " ")}
                </div>
                <div className="text-xs text-emerald-600 font-semibold mt-0.5">Best validation performer</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Projection Span</span>
                <div className="text-sm font-bold text-slate-800 mt-1 truncate">{forecastResult.start_date}</div>
                <div className="text-xs text-slate-500 truncate">to {forecastResult.end_date}</div>
              </div>
            </div>

            {/* Interactive Forecast Chart */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-slate-900 text-base">Historical Actuals vs Forecast Horizon</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Shaded area represents the {(forecastResult.confidence_level * 100).toFixed(0)}% empirical prediction interval.
                  </p>
                </div>
              </div>

              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} tickMargin={8} />
                    <YAxis stroke="#94a3b8" fontSize={11} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", color: "#fff", border: "none" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
                    <Line
                      type="monotone"
                      dataKey="historical"
                      name="Historical Actuals"
                      stroke="#64748b"
                      strokeWidth={2}
                      dot={false}
                    />
                    <Area
                      type="monotone"
                      dataKey="upper"
                      name="Upper Prediction Bound"
                      fill="#bfdbfe"
                      stroke="#93c5fd"
                      fillOpacity={0.4}
                    />
                    <Line
                      type="monotone"
                      dataKey="predicted"
                      name="Predicted Demand"
                      stroke="#2563eb"
                      strokeWidth={3}
                      dot={{ r: 3 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="lower"
                      name="Lower Bound"
                      stroke="#93c5fd"
                      strokeDasharray="3 3"
                      strokeWidth={1}
                      dot={false}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Forecast Points Sample Table */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-900 text-base">Product-Level Forecast Points</h3>
                <span className="text-xs text-slate-500">First 20 items</span>
              </div>
              <div className="overflow-x-auto max-h-72 border border-slate-200 rounded-lg">
                <table className="w-full text-xs text-left text-slate-700">
                  <thead className="bg-slate-100 font-semibold text-slate-900 border-b border-slate-200">
                    <tr>
                      <th className="px-3 py-2.5">Date</th>
                      <th className="px-3 py-2.5">SKU / Product ID</th>
                      <th className="px-3 py-2.5">Store</th>
                      <th className="px-3 py-2.5 text-right font-bold text-blue-700">Predicted Demand</th>
                      <th className="px-3 py-2.5 text-right">Lower Bound</th>
                      <th className="px-3 py-2.5 text-right">Upper Bound</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {forecastResult.forecast_points_sample.slice(0, 20).map((pt, idx) => (
                      <tr key={idx} className="hover:bg-slate-50">
                        <td className="px-3 py-2 font-mono">{pt.date}</td>
                        <td className="px-3 py-2 font-bold text-slate-900">{pt.product_id}</td>
                        <td className="px-3 py-2">{pt.store_id || "ALL"}</td>
                        <td className="px-3 py-2 text-right font-bold text-blue-700">{pt.predicted_demand.toFixed(1)}</td>
                        <td className="px-3 py-2 text-right text-slate-500">{pt.lower_bound.toFixed(1)}</td>
                        <td className="px-3 py-2 text-right text-slate-500">{pt.upper_bound.toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

function intPercentage(val: number) {
  return Math.round(val * 100);
}

