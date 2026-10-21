"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, TrainingJob } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import {
  Cpu,
  Play,
  CheckCircle2,
  AlertCircle,
  Sliders,
  Layers,
  ArrowRight,
  TrendingUp,
  RefreshCw
} from "lucide-react";

const AVAILABLE_MODELS = [
  { id: "naive", name: "Naive Baseline", desc: "Last observed sales (lag_1)" },
  { id: "seasonal_naive", name: "Seasonal Naive", desc: "Weekly seasonal pattern (lag_7)" },
  { id: "linear_regression", name: "Linear Regression (Ridge)", desc: "L2 Regularized linear model" },
  { id: "random_forest", name: "Random Forest", desc: "Ensemble of bagging decision trees" },
  { id: "xgboost", name: "XGBoost", desc: "Extreme gradient boosted decision trees" },
  { id: "lightgbm", name: "LightGBM", desc: "High-performance histogram gradient boosting" },
];

export default function TrainingPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string>("");
  const [selectedModels, setSelectedModels] = useState<string[]>([
    "naive",
    "seasonal_naive",
    "linear_regression",
    "xgboost",
    "lightgbm"
  ]);
  const [horizonDays, setHorizonDays] = useState<number>(14);
  const [validationDays, setValidationDays] = useState<number>(14);

  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<TrainingJob | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getDatasets().then((list) => {
      setDatasets(list);
      if (list.length > 0) setSelectedDatasetId(list[0].id);
    });
  }, []);

  // Poll active training job
  useEffect(() => {
    if (!activeJobId) return;

    const interval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(activeJobId);
        setJobStatus(job);
        if (job.status === "COMPLETED" || job.status === "FAILED") {
          clearInterval(interval);
        }
      } catch (err) {
        console.error("Job status polling error:", err);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeJobId]);

  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      if (selectedModels.length > 1) {
        setSelectedModels(selectedModels.filter((m) => m !== modelId));
      }
    } else {
      setSelectedModels([...selectedModels, modelId]);
    }
  };

  const handleStartTraining = async () => {
    if (!selectedDatasetId) return;
    setIsSubmitting(true);
    setError(null);

    try {
      const res = await api.startTraining(selectedDatasetId, {
        models: selectedModels,
        horizon_days: horizonDays,
        validation_days: validationDays,
      });
      setActiveJobId(res.job_id);
    } catch (err: any) {
      setError(err.message || "Failed to launch training job.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AppShell title="Model Training & Pipeline Orchestration">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Train &amp; Compare Models</h1>
          <p className="text-sm text-slate-500 mt-1">
            Execute chronological splits, feature engineering, and evaluate candidate algorithms on out-of-sample data.
          </p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Training Configuration Panel */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
            <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
              <Sliders className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-base">Training Configuration</h3>
            </div>

            {/* Dataset Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Target Dataset</label>
              <select
                value={selectedDatasetId}
                onChange={(e) => setSelectedDatasetId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white font-medium text-slate-900 focus:ring-2 focus:ring-blue-500"
              >
                {datasets.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.row_count} rows)
                  </option>
                ))}
              </select>
            </div>

            {/* Model Selection Checkboxes */}
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-2">Candidate Forecasters</label>
              <div className="space-y-2">
                {AVAILABLE_MODELS.map((m) => {
                  const checked = selectedModels.includes(m.id);
                  return (
                    <div
                      key={m.id}
                      onClick={() => toggleModel(m.id)}
                      className={`p-3 rounded-lg border cursor-pointer transition-all flex items-start space-x-3 ${
                        checked ? "bg-blue-50/70 border-blue-500" : "bg-slate-50 border-slate-200"
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => {}}
                        className="mt-0.5 rounded text-blue-600 focus:ring-blue-500"
                      />
                      <div className="text-xs">
                        <div className="font-bold text-slate-900">{m.name}</div>
                        <div className="text-slate-500 text-[11px]">{m.desc}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Horizon & Validation sliders */}
            <div className="space-y-4 pt-2 border-t border-slate-100">
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                  <span>Forecast Horizon:</span>
                  <span className="text-blue-600">{horizonDays} Days</span>
                </div>
                <input
                  type="range"
                  min="7"
                  max="60"
                  step="7"
                  value={horizonDays}
                  onChange={(e) => setHorizonDays(Number(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-600 mb-1">
                  <span>Validation Window:</span>
                  <span className="text-blue-600">{validationDays} Days</span>
                </div>
                <input
                  type="range"
                  min="7"
                  max="30"
                  step="7"
                  value={validationDays}
                  onChange={(e) => setValidationDays(Number(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
            </div>

            <button
              onClick={handleStartTraining}
              disabled={isSubmitting || (jobStatus?.status === "RUNNING")}
              className="w-full py-3 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm transition-all shadow-md shadow-blue-500/25 flex items-center justify-center space-x-2 disabled:bg-slate-300"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{jobStatus?.status === "RUNNING" ? "Training in progress..." : "Initiate Model Training"}</span>
            </button>
          </div>

          {/* Job Execution & Live Results Area */}
          <div className="lg:col-span-2 space-y-6">
            {jobStatus ? (
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
                <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">Active Execution Workflow</h3>
                    <p className="text-xs text-slate-400 mt-0.5">Job ID: {jobStatus.job_id.slice(0, 16)}...</p>
                  </div>
                  <StatusBadge status={jobStatus.status} />
                </div>

                {/* Progress bar */}
                <div>
                  <div className="flex justify-between text-xs font-semibold text-slate-700 mb-2">
                    <span>{jobStatus.current_step}</span>
                    <span>{jobStatus.progress_pct}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                    <div
                      className={`h-2.5 rounded-full transition-all duration-500 ${
                        jobStatus.status === "FAILED" ? "bg-rose-500" : "bg-blue-600"
                      }`}
                      style={{ width: `${jobStatus.progress_pct}%` }}
                    ></div>
                  </div>
                </div>

                {jobStatus.error_message && (
                  <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-lg">
                    {jobStatus.error_message}
                  </div>
                )}

                {/* Trained Models Results Table */}
                {jobStatus.models && jobStatus.models.length > 0 && (
                  <div className="pt-2">
                    <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                      Trained Models &amp; Test Performance
                    </h4>
                    <div className="border border-slate-200 rounded-lg overflow-hidden">
                      <table className="w-full text-xs text-left text-slate-700">
                        <thead className="bg-slate-100 font-semibold text-slate-900 border-b border-slate-200">
                          <tr>
                            <th className="px-3 py-2.5">Model</th>
                            <th className="px-3 py-2.5">Type</th>
                            <th className="px-3 py-2.5">WAPE</th>
                            <th className="px-3 py-2.5">MAE</th>
                            <th className="px-3 py-2.5">RMSE</th>
                            <th className="px-3 py-2.5">Bias</th>
                            <th className="px-3 py-2.5">Status</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {jobStatus.models.map((m) => (
                            <tr key={m.id} className={m.is_best ? "bg-emerald-50/40" : "hover:bg-slate-50"}>
                              <td className="px-3 py-2.5 font-bold text-slate-900">
                                {m.model_name.toUpperCase()}
                              </td>
                              <td className="px-3 py-2.5 uppercase text-[10px] text-slate-500">{m.model_type}</td>
                              <td className="px-3 py-2.5 font-semibold text-slate-900">
                                {(m.metrics.wape * 100).toFixed(1)}%
                              </td>
                              <td className="px-3 py-2.5">{m.metrics.mae.toFixed(2)}</td>
                              <td className="px-3 py-2.5">{m.metrics.rmse.toFixed(2)}</td>
                              <td className="px-3 py-2.5">{(m.metrics.bias * 100).toFixed(1)}%</td>
                              <td className="px-3 py-2.5">
                                {m.is_best ? (
                                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                                    BEST MODEL
                                  </span>
                                ) : (
                                  <span className="text-slate-400 text-[10px]">Evaluated</span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {jobStatus.status === "COMPLETED" && (
                      <div className="mt-4 flex justify-end">
                        <Link
                          href="/forecasts"
                          className="inline-flex items-center space-x-1.5 px-4 py-2 text-xs font-semibold rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white transition-colors shadow-sm"
                        >
                          <span>Proceed to Forecast Generation</span>
                          <ArrowRight className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-500">
                <Cpu className="w-12 h-12 mx-auto text-slate-400 mb-3" />
                <h3 className="font-semibold text-slate-800 text-base">Ready to Train</h3>
                <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
                  Select candidate models and click &quot;Initiate Model Training&quot; to execute the pipeline.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}

