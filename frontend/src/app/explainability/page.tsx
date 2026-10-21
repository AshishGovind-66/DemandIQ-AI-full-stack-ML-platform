"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, TrainedModel, ShapExplanationResponse } from "@/types";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";
import {
  BrainCircuit,
  Sparkles,
  Info,
  AlertCircle,
  HelpCircle,
  Sliders,
  CheckCircle2
} from "lucide-react";

export default function ExplainabilityPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [models, setModels] = useState<TrainedModel[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<string>("");
  const [shapResult, setShapResult] = useState<ShapExplanationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) setSelectedDatasetId(list[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) return;
    api.getModelComparison(selectedDatasetId).then((res) => {
      setModels(res.models || []);
      if (res.models && res.models.length > 0) {
        // Prefer best model or first ML model
        const best = res.models.find((m) => m.is_best) || res.models[0];
        setSelectedModelId(best.id);
      }
    });
  }, [selectedDatasetId]);

  const handleComputeShap = async () => {
    if (!selectedModelId) return;
    setLoading(true);
    setError(null);

    try {
      const res = await api.getShapExplanations(selectedModelId, 150);
      setShapResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to calculate SHAP attributions.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell title="Explainable AI & Feature Drivers (SHAP)">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Controls Card */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">Model Interpretability Engine</h1>
              <p className="text-xs text-slate-500 mt-0.5">
                Shapley Additive exPlanations (SHAP) attributing demand drivers across tree and linear models.
              </p>
            </div>

            <button
              onClick={handleComputeShap}
              disabled={loading || !selectedModelId}
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all shadow-md shadow-blue-500/25 disabled:bg-slate-300"
            >
              <BrainCircuit className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              <span>{loading ? "Computing Attributions..." : "Calculate SHAP Values"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-100 text-xs">
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
              <label className="block font-semibold text-slate-600 mb-1">Model to Explain</label>
              <select
                value={selectedModelId}
                onChange={(e) => setSelectedModelId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
              >
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.model_name.toUpperCase()} ({m.model_type}) {m.is_best ? "— LEADER" : ""}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {shapResult && (
          <div className="space-y-6">
            {!shapResult.is_supported ? (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-5 text-amber-900 text-sm">
                <div className="font-bold flex items-center space-x-2">
                  <Info className="w-5 h-5 text-amber-600" />
                  <span>Model Type Limitation</span>
                </div>
                <p className="mt-2 text-xs leading-relaxed">{shapResult.summary_message}</p>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Methodological Caution Alert */}
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-900 flex items-start space-x-3">
                  <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold">Interpretability Note:</span> SHAP values reflect the marginal
                    contribution of each feature to the model&apos;s decision trees. They quantify statistical attribution,
                    not causal mechanics.
                  </div>
                </div>

                {/* Global Feature Importance Chart */}
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-bold text-slate-900 text-base">Global Feature Importance (Mean |SHAP|)</h3>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Attribution weight of features across evaluated demand predictions.
                      </p>
                    </div>
                  </div>

                  <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={shapResult.global_feature_importance}
                        layout="vertical"
                        margin={{ left: 30, right: 30 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis type="number" stroke="#94a3b8" fontSize={11} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                        <YAxis type="category" dataKey="feature" stroke="#94a3b8" fontSize={11} width={120} />
                        <Tooltip
                          contentStyle={{ backgroundColor: "#0f172a", borderRadius: "8px", color: "#fff", border: "none" }}
                          formatter={(val: any) => [`${(Number(val) * 100).toFixed(1)}%`, "Attribution"]}
                        />
                        <Bar dataKey="importance" fill="#2563eb" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Key Takeaways & Feature Drivers */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
                    <h3 className="font-bold text-slate-900 text-sm">Key Demand Driver Insights</h3>
                    <div className="space-y-2 text-xs text-slate-600">
                      {shapResult.top_drivers_summary.map((driver, idx) => (
                        <div key={idx} className="flex items-start space-x-2 bg-slate-50 p-3 rounded-lg border border-slate-100">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                          <span>{driver}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
                    <h3 className="font-bold text-slate-900 text-sm">Feature Dictionary</h3>
                    <div className="divide-y divide-slate-100 text-xs max-h-56 overflow-y-auto">
                      {shapResult.global_feature_importance.map((item) => (
                        <div key={item.feature} className="py-2 flex justify-between">
                          <span className="font-mono font-bold text-slate-800">{item.feature}</span>
                          <span className="text-slate-500 text-right">{item.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}

