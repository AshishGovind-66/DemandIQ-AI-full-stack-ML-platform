"use client";

import { useEffect, useState, useRef } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Dataset, ValidationResult, ColumnMappingConfig } from "@/types";
import {
  Database,
  Upload,
  Layers,
  CheckCircle2,
  AlertCircle,
  FileText,
  RefreshCw,
  Table,
  Sliders,
  Sparkles
} from "lucide-react";

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [extractingM5, setExtractingM5] = useState(false);
  const [previewData, setPreviewData] = useState<{ columns: string[]; rows: any[] } | null>(null);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Column mapping form state
  const [mapping, setMapping] = useState<ColumnMappingConfig>({
    date_col: "date",
    target_col: "sales",
    product_id_col: "product_id",
    store_id_col: "store_id",
    category_col: "category",
    price_col: "sell_price",
    promo_col: "on_promotion"
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDatasets = async () => {
    setLoading(true);
    try {
      const list = await api.getDatasets();
      setDatasets(list);
      if (list.length > 0 && !selectedDataset) {
        selectDataset(list[0]);
      }
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "Failed to load datasets." });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const selectDataset = async (dataset: Dataset) => {
    setSelectedDataset(dataset);
    setValidationResult(null);
    setNotification(null);

    // Populate mapping state from dataset
    if (dataset.column_mapping) {
      setMapping({
        date_col: dataset.column_mapping.date_col || "date",
        target_col: dataset.column_mapping.target_col || "sales",
        product_id_col: dataset.column_mapping.product_id_col || "product_id",
        store_id_col: dataset.column_mapping.store_id_col || "store_id",
        category_col: dataset.column_mapping.category_col || "category",
        price_col: dataset.column_mapping.price_col || "sell_price",
        promo_col: dataset.column_mapping.promo_col || "on_promotion",
      });
    }

    // Load preview
    try {
      const prev = await api.previewDataset(dataset.id, 15);
      setPreviewData(prev);
    } catch {
      setPreviewData(null);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setNotification(null);
    try {
      const newDataset = await api.uploadDataset(file);
      setNotification({ type: "success", message: `Dataset '${newDataset.name}' uploaded successfully!` });
      await fetchDatasets();
      selectDataset(newDataset);
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "Upload failed." });
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleExtractM5 = async () => {
    setExtractingM5(true);
    setNotification(null);
    try {
      const m5Subset = await api.extractM5Subset(["CA_1"], 15, 180);
      setNotification({ type: "success", message: `Extracted Walmart M5 subset (${m5Subset.row_count} rows)!` });
      await fetchDatasets();
      selectDataset(m5Subset);
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "M5 extraction failed. Ensure M5 raw files exist." });
    } finally {
      setExtractingM5(false);
    }
  };

  const handleValidateAndMap = async () => {
    if (!selectedDataset) return;
    try {
      const val = await api.validateDataset(selectedDataset.id, mapping);
      setValidationResult(val);
      if (val.is_valid) {
        await api.updateColumnMapping(selectedDataset.id, mapping);
        setNotification({ type: "success", message: "Schema validated and standardized successfully!" });
        fetchDatasets();
      } else {
        setNotification({ type: "error", message: "Dataset has validation errors. Review issues below." });
      }
    } catch (err: any) {
      setNotification({ type: "error", message: err.message || "Validation failed." });
    }
  };

  return (
    <AppShell title="Dataset Management & Profiling">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Header Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Dataset Hub</h1>
            <p className="text-sm text-slate-500 mt-1">
              Upload retail sales CSVs, auto-detect columns, or extract manageable slices of the Walmart M5 dataset.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleExtractM5}
              disabled={extractingM5}
              className="inline-flex items-center space-x-2 px-3.5 py-2 text-sm font-medium rounded-lg border border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 transition-colors shadow-sm"
            >
              <Sparkles className={`w-4 h-4 ${extractingM5 ? "animate-spin" : "text-blue-600"}`} />
              <span>{extractingM5 ? "Extracting M5..." : "Extract M5 Subset"}</span>
            </button>

            <label className="inline-flex items-center space-x-2 px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 hover:bg-blue-700 text-white cursor-pointer shadow-sm transition-colors">
              <Upload className="w-4 h-4" />
              <span>{uploading ? "Uploading..." : "Upload CSV"}</span>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </label>
          </div>
        </div>

        {notification && (
          <div
            className={`p-4 rounded-xl border text-sm flex items-center space-x-3 ${
              notification.type === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                : "bg-rose-50 border-rose-200 text-rose-800"
            }`}
          >
            {notification.type === "success" ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
            )}
            <span>{notification.message}</span>
          </div>
        )}

        {/* Dataset Selection Tabs / Grid */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">Available Datasets</h3>
            <span className="text-xs text-slate-400">{datasets.length} registered</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {datasets.map((d) => {
              const isSelected = selectedDataset?.id === d.id;
              return (
                <button
                  key={d.id}
                  onClick={() => selectDataset(d)}
                  className={`text-left p-3.5 rounded-lg border transition-all ${
                    isSelected
                      ? "bg-blue-50/60 border-blue-500 shadow-sm ring-1 ring-blue-500"
                      : "bg-slate-50/50 border-slate-200 hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-sm text-slate-900 truncate max-w-[200px]">{d.name}</span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                      {d.file_type}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{d.row_count.toLocaleString()} rows</span>
                    <span>{d.column_count} cols</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {selectedDataset && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Column Mapping Form */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
                <Sliders className="w-5 h-5 text-blue-600" />
                <h3 className="font-bold text-slate-900 text-base">Schema &amp; Column Mapping</h3>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Date Column *</label>
                  <select
                    value={mapping.date_col}
                    onChange={(e) => setMapping({ ...mapping, date_col: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
                  >
                    {selectedDataset.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Demand / Sales Column *</label>
                  <select
                    value={mapping.target_col}
                    onChange={(e) => setMapping({ ...mapping, target_col: e.target.value })}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
                  >
                    {selectedDataset.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Product ID Column</label>
                  <select
                    value={mapping.product_id_col || ""}
                    onChange={(e) => setMapping({ ...mapping, product_id_col: e.target.value || undefined })}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">None (Single Product)</option>
                    {selectedDataset.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Store / Location Column</label>
                  <select
                    value={mapping.store_id_col || ""}
                    onChange={(e) => setMapping({ ...mapping, store_id_col: e.target.value || undefined })}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">None (Single Store)</option>
                    {selectedDataset.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Sell Price Column</label>
                  <select
                    value={mapping.price_col || ""}
                    onChange={(e) => setMapping({ ...mapping, price_col: e.target.value || undefined })}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm bg-white text-slate-900 focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">None (Default $1.00)</option>
                    {selectedDataset.columns.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={handleValidateAndMap}
                className="w-full mt-4 py-2.5 px-4 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-medium text-sm transition-colors shadow-sm"
              >
                Validate &amp; Standardize Schema
              </button>
            </div>

            {/* Validation & Preview Section */}
            <div className="lg:col-span-2 space-y-6">
              {/* Validation Results Card */}
              {validationResult && (
                <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-slate-900 text-base">Validation Report</h3>
                    <span
                      className={`px-2.5 py-1 rounded text-xs font-bold ${
                        validationResult.is_valid
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-rose-100 text-rose-800"
                      }`}
                    >
                      {validationResult.is_valid ? "VALID FOR FORECASTING" : "INVALID SCHEMA"}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {validationResult.issues.map((iss, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg text-xs flex items-start space-x-2 border ${
                          iss.severity === "ERROR"
                            ? "bg-rose-50 border-rose-200 text-rose-800"
                            : iss.severity === "WARNING"
                            ? "bg-amber-50 border-amber-200 text-amber-800"
                            : "bg-blue-50 border-blue-200 text-blue-800"
                        }`}
                      >
                        <span className="font-bold uppercase text-[10px] mt-0.5">[{iss.severity}]</span>
                        <span>{iss.message}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Data Preview Table */}
              <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <Table className="w-5 h-5 text-slate-500" />
                    <h3 className="font-bold text-slate-900 text-base">Raw Data Preview</h3>
                  </div>
                  <span className="text-xs text-slate-500">First 15 observations</span>
                </div>

                {previewData && previewData.rows.length > 0 ? (
                  <div className="overflow-x-auto max-h-72 border border-slate-200 rounded-lg">
                    <table className="w-full text-xs text-left text-slate-700">
                      <thead className="bg-slate-100 text-slate-900 sticky top-0 font-semibold border-b border-slate-200">
                        <tr>
                          {previewData.columns.slice(0, 8).map((col) => (
                            <th key={col} className="px-3 py-2 whitespace-nowrap">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {previewData.rows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-slate-50">
                            {previewData.columns.slice(0, 8).map((col) => (
                              <td key={col} className="px-3 py-2 whitespace-nowrap">
                                {String(row[col])}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-sm text-slate-400 py-8 text-center">Loading preview data...</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

