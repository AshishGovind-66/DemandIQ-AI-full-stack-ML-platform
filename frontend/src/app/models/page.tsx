"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, TrainedModel } from "@/types";
import {
  Trophy,
  Sliders,
  ArrowRight,
  TrendingUp,
  BrainCircuit,
  Info
} from "lucide-react";

export default function ModelsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [models, setModels] = useState<TrainedModel[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeParamModel, setActiveParamModel] = useState<TrainedModel | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) setSelectedDatasetId(list[0].id);
    });
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) return;
    setLoading(true);
    api
      .getModelComparison(selectedDatasetId)
      .then((res) => {
        setModels(res.models || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [selectedDatasetId]);

  return (
    <AppShell title="Model Leaderboard & Evaluation">
      <div className="space-y-6 max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">Forecaster Leaderboard</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Ranked out-of-sample performance across baselines and machine learning algorithms.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-semibold text-slate-600">Dataset:</span>
            <select
              value={selectedDatasetId}
              onChange={(e) => setSelectedDatasetId(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Comparison Table */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-slate-400">Loading model performance benchmarks...</div>
          ) : models.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left text-slate-700">
                <thead className="bg-slate-100 font-semibold text-slate-900 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3">Rank / Status</th>
                    <th className="px-4 py-3">Model</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3">WAPE</th>
                    <th className="px-4 py-3">MAE</th>
                    <th className="px-4 py-3">RMSE</th>
                    <th className="px-4 py-3">Forecast Bias</th>
                    <th className="px-4 py-3">Parameters</th>
                    <th className="px-4 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {models.map((m, idx) => (
                    <tr key={m.id} className={m.is_best ? "bg-emerald-50/50" : "hover:bg-slate-50"}>
                      <td className="px-4 py-3.5">
                        {m.is_best ? (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-200">
                            <Trophy className="w-3 h-3 text-emerald-700" />
                            <span>BEST MODEL</span>
                          </span>
                        ) : (
                          <span className="text-slate-400 font-semibold">#{idx + 1}</span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 font-bold text-slate-900 uppercase">
                        {m.model_name.replace("_", " ")}
                      </td>
                      <td className="px-4 py-3.5 uppercase text-[10px] text-slate-500">{m.model_type}</td>
                      <td className="px-4 py-3.5 font-bold text-slate-900">
                        {m.metrics ? `${(m.metrics.wape * 100).toFixed(1)}%` : "N/A"}
                      </td>
                      <td className="px-4 py-3.5">{m.metrics ? m.metrics.mae.toFixed(2) : "N/A"}</td>
                      <td className="px-4 py-3.5">{m.metrics ? m.metrics.rmse.toFixed(2) : "N/A"}</td>
                      <td className="px-4 py-3.5">
                        {m.metrics ? (
                          <span
                            className={
                              m.metrics.bias > 0.05
                                ? "text-amber-700 font-semibold"
                                : m.metrics.bias < -0.05
                                ? "text-blue-700 font-semibold"
                                : "text-slate-600"
                            }
                          >
                            {(m.metrics.bias * 100).toFixed(1)}% {m.metrics.bias > 0 ? "(Over)" : "(Under)"}
                          </span>
                        ) : (
                          "N/A"
                        )}
                      </td>
                      <td className="px-4 py-3.5">
                        <button
                          onClick={() => setActiveParamModel(m)}
                          className="text-blue-600 hover:text-blue-800 underline font-medium text-[11px]"
                        >
                          View Config
                        </button>
                      </td>
                      <td className="px-4 py-3.5 text-right space-x-2">
                        <Link
                          href={`/explainability`}
                          className="inline-flex items-center space-x-1 text-slate-600 hover:text-blue-600 font-medium"
                        >
                          <BrainCircuit className="w-3.5 h-3.5" />
                          <span>Explain</span>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center text-sm text-slate-500">
              No models have been trained for this dataset yet. Go to Model Training to evaluate forecasters.
            </div>
          )}
        </div>

        {/* Parameters Modal */}
        {activeParamModel && (
          <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h3 className="font-bold text-slate-900 text-base uppercase">
                  {activeParamModel.model_name.replace("_", " ")} Hyperparameters
                </h3>
                <button
                  onClick={() => setActiveParamModel(null)}
                  className="text-slate-400 hover:text-slate-600 text-lg font-bold"
                >
                  &times;
                </button>
              </div>

              <div className="mt-4 bg-slate-50 p-4 rounded-lg text-xs font-mono overflow-x-auto max-h-60 border border-slate-100">
                <pre>{JSON.stringify(activeParamModel.parameters, null, 2)}</pre>
              </div>

              <div className="mt-5 flex justify-end">
                <button
                  onClick={() => setActiveParamModel(null)}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

