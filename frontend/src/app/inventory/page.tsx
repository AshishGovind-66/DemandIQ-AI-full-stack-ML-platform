"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, InventoryOptimizationSummary } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  PackageCheck,
  AlertTriangle,
  Archive,
  DollarSign,
  Download,
  Sliders,
  Sparkles,
  Info,
  ArrowRight,
  ShieldAlert
} from "lucide-react";

export default function InventoryPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [leadTimeDays, setLeadTimeDays] = useState<number>(7);
  const [serviceLevel, setServiceLevel] = useState<number>(0.95);
  const [minOrderQty, setMinOrderQty] = useState<number>(5);
  const [packSize, setPackSize] = useState<number>(1);
  const [defaultStock, setDefaultStock] = useState<number>(20);

  const [summary, setSummary] = useState<InventoryOptimizationSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) setSelectedDatasetId(list[0].id);
    });
  }, []);

  const handleOptimize = async () => {
    if (!selectedDatasetId) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.optimizeInventory({
        dataset_id: selectedDatasetId,
        lead_time_days: leadTimeDays,
        service_level: serviceLevel,
        min_order_quantity: minOrderQty,
        pack_size: packSize,
        default_current_stock: defaultStock,
      });
      setSummary(res);
    } catch (err: any) {
      setError(err.message || "Failed to run inventory optimization.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Supply Chain & Inventory Optimization Engine">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Controls Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Stock Optimization &amp; Replenishment</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Calculates mathematical Safety Stock (SS), Reorder Points (ROP), and Order Quantities under MOQ constraints.
              </p>
            </div>

            <button
              onClick={handleOptimize}
              disabled={loading || !selectedDatasetId}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all shadow-md shadow-blue-500/25 disabled:bg-slate-300"
            >
              <PackageCheck className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Calculating Policies..." : "Optimize Inventory"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 pt-3 border-t border-slate-100 text-xs">
            <div>
              <label className="block font-semibold text-slate-600 mb-1">Target Dataset</label>
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1.5">Cycle Service Level (CSL)</label>
              <div className="flex rounded-lg border border-slate-200 p-0.5 bg-slate-50">
                {[0.90, 0.95, 0.98, 0.99].map((sl) => (
                  <button
                    key={sl}
                    onClick={() => setServiceLevel(sl)}
                    className={`flex-1 py-1.5 font-semibold rounded-md transition-all ${
                      serviceLevel === sl ? "bg-white text-blue-600 shadow-sm" : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    {(sl * 100).toFixed(0)}%
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1">Supplier Lead Time (Days)</label>
              <input
                type="number"
                min="1"
                max="90"
                value={leadTimeDays}
                onChange={(e) => setLeadTimeDays(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1">Min Order Qty (MOQ)</label>
              <input
                type="number"
                min="1"
                max="500"
                value={minOrderQty}
                onChange={(e) => setMinOrderQty(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block font-semibold text-slate-600 mb-1">Pack Size Multiple</label>
              <input
                type="number"
                min="1"
                max="100"
                value={packSize}
                onChange={(e) => setPackSize(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {summary && (
          <div className="space-y-6">
            {/* KPI Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Products Analyzed</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">{summary.total_products_analyzed}</div>
                <div className="text-xs text-slate-400 mt-0.5">CSL: {(summary.service_level * 100).toFixed(0)}%</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-rose-200 shadow-sm bg-rose-50/20">
                <span className="text-[11px] font-semibold uppercase text-rose-600">Stockout Risk Items</span>
                <div className="text-2xl font-bold text-rose-700 mt-1">{summary.items_at_stockout_risk}</div>
                <div className="text-xs text-rose-600 mt-0.5">Stock below Reorder Point</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Excess Stock Items</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">{summary.items_with_excess_stock}</div>
                <div className="text-xs text-slate-400 mt-0.5">Cover &gt; 60 days</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Suggested Order Units</span>
                <div className="text-2xl font-bold text-blue-600 mt-1">
                  {summary.total_suggested_reorder_units.toLocaleString()}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Replenishment batch</div>
              </div>

              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-[11px] font-semibold uppercase text-slate-500">Estimated Reorder Cost</span>
                <div className="text-2xl font-bold text-slate-900 mt-1">
                  ${summary.total_estimated_reorder_value.toLocaleString()}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">Based on unit costs</div>
              </div>
            </div>

            {/* Inventory Policy Formula Banner */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start space-x-3">
              <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Inventory Policy Formula:</span> Safety Stock{" "}
                <code className="bg-blue-100 px-1 py-0.5 rounded font-mono">SS = z × σ_D × √L</code> | Reorder Point{" "}
                <code className="bg-blue-100 px-1 py-0.5 rounded font-mono">ROP = LTD + SS</code> | Replenishment Order{" "}
                <code className="bg-blue-100 px-1 py-0.5 rounded font-mono">Order = max(0, Target - IP)</code>.
                Quantities are rounded up to MOQ and Pack Size constraints.
              </div>
            </div>

            {/* Recommendations Table */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-slate-900 text-sm">Product-Level Replenishment Recommendations</h3>
                  <p className="text-xs text-slate-500 mt-0.5">Actionable procurement decisions per SKU</p>
                </div>

                <Link
                  href="/reports"
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 bg-white hover:bg-slate-50 text-xs font-semibold shadow-sm transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Report CSV</span>
                </Link>
              </div>

              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-xs text-left text-slate-700">
                  <thead className="bg-slate-100 font-semibold text-slate-900 border-b border-slate-200 sticky top-0">
                    <tr>
                      <th className="px-3 py-2.5">SKU / Item</th>
                      <th className="px-3 py-2.5">Daily Mean (μ)</th>
                      <th className="px-3 py-2.5">Daily Volatility (σ)</th>
                      <th className="px-3 py-2.5">Safety Stock</th>
                      <th className="px-3 py-2.5 font-bold">Reorder Point (ROP)</th>
                      <th className="px-3 py-2.5">Current Stock</th>
                      <th className="px-3 py-2.5 text-right font-bold text-blue-700">Suggested Order Qty</th>
                      <th className="px-3 py-2.5">Supply Remaining</th>
                      <th className="px-3 py-2.5">Stock Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {summary.recommendations.map((rec) => (
                      <tr
                        key={rec.product_id}
                        className={rec.stockout_risk ? "bg-rose-50/40 hover:bg-rose-50/60" : "hover:bg-slate-50"}
                      >
                        <td className="px-3 py-2 font-bold text-slate-900">{rec.product_id}</td>
                        <td className="px-3 py-2">{rec.daily_demand_mean.toFixed(1)}</td>
                        <td className="px-3 py-2">{rec.daily_demand_std.toFixed(1)}</td>
                        <td className="px-3 py-2">{rec.safety_stock.toFixed(1)}</td>
                        <td className="px-3 py-2 font-bold text-slate-900">{rec.reorder_point.toFixed(1)}</td>
                        <td className="px-3 py-2">{rec.current_on_hand.toFixed(1)}</td>
                        <td className="px-3 py-2 text-right font-bold text-blue-700">
                          {rec.suggested_order_qty > 0 ? (
                            <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-mono">
                              +{rec.suggested_order_qty}
                            </span>
                          ) : (
                            <span className="text-slate-400">0</span>
                          )}
                        </td>
                        <td className="px-3 py-2">{rec.days_of_supply_remaining.toFixed(1)} days</td>
                        <td className="px-3 py-2">
                          {rec.stockout_risk ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-100 text-rose-800 border border-rose-200">
                              REORDER NOW
                            </span>
                          ) : rec.excess_stock_risk ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-200">
                              EXCESS STOCK
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                              OPTIMAL
                            </span>
                          )}
                        </td>
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

