import {
  HealthResponse,
  DashboardSummary,
  Dataset,
  ValidationResult,
  ColumnMappingConfig,
  DataProfilingReport,
  TrainingJob,
  TrainedModel,
  ForecastResponse,
  InventoryOptimizationSummary,
  ShapExplanationResponse
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${endpoint}`;
  const headers = {
    ...(!options.body || !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
    ...options.headers,
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}`;
      try {
        const errJson = await res.json();
        errorMsg = errJson.detail || errJson.error || errorMsg;
      } catch {
        // fallback
      }
      throw new Error(errorMsg);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => request<HealthResponse>("/health"),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>("/api/v1/dashboard/summary"),

  // Datasets
  getDatasets: () => request<Dataset[]>("/api/v1/datasets"),
  getDataset: (id: string) => request<Dataset>(`/api/v1/datasets/${id}`),
  previewDataset: (id: string, limit: number = 30) =>
    request<{ dataset_id: string; columns: string[]; rows: Record<string, any>[] }>(
      `/api/v1/datasets/${id}/preview?limit=${limit}`
    ),
  uploadDataset: async (file: File, datasetName?: string): Promise<Dataset> => {
    const formData = new FormData();
    formData.append("file", file);
    if (datasetName) formData.append("dataset_name", datasetName);
    return request<Dataset>("/api/v1/datasets/upload", {
      method: "POST",
      body: formData,
    });
  },
  validateDataset: (id: string, mapping?: ColumnMappingConfig) =>
    request<ValidationResult>(`/api/v1/datasets/${id}/validate`, {
      method: "POST",
      body: mapping ? JSON.stringify(mapping) : undefined,
    }),
  updateColumnMapping: (id: string, mapping: ColumnMappingConfig) =>
    request<Dataset>(`/api/v1/datasets/${id}/map-columns`, {
      method: "POST",
      body: JSON.stringify(mapping),
    }),
  getDatasetProfile: (id: string) => request<DataProfilingReport>(`/api/v1/datasets/${id}/profile`),
  extractM5Subset: (storeIds: string[], itemLimit: number = 20, daysLimit: number = 180) =>
    request<Dataset>("/api/v1/datasets/m5/extract", {
      method: "POST",
      body: JSON.stringify({ store_ids: storeIds, item_limit: itemLimit, days_limit: daysLimit }),
    }),

  // Training & Models
  startTraining: (
    datasetId: string,
    params: { models: string[]; horizon_days: number; validation_days: number; product_ids?: string[] }
  ) =>
    request<{ job_id: string; dataset_id: string; status: string; message: string }>(
      `/api/v1/datasets/${datasetId}/train`,
      {
        method: "POST",
        body: JSON.stringify(params),
      }
    ),
  getJobStatus: (jobId: string) => request<TrainingJob>(`/api/v1/jobs/${jobId}`),
  getModelComparison: (datasetId: string) =>
    request<{ dataset_id: string; models: TrainedModel[] }>(`/api/v1/models/comparison/${datasetId}`),
  getModelDetail: (modelId: string) => request<TrainedModel>(`/api/v1/models/${modelId}`),

  // Forecasting
  generateForecast: (params: {
    dataset_id: string;
    model_id?: string;
    horizon_days: number;
    confidence_level?: number;
    product_ids?: string[];
  }) =>
    request<ForecastResponse>("/api/v1/forecasts/generate", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  // Inventory Optimization
  optimizeInventory: (params: {
    dataset_id: string;
    forecast_run_id?: string;
    lead_time_days: number;
    service_level: number;
    default_current_stock?: number;
    min_order_quantity?: number;
    pack_size?: number;
  }) =>
    request<InventoryOptimizationSummary>("/api/v1/inventory/optimize", {
      method: "POST",
      body: JSON.stringify(params),
    }),

  // Explainability
  getShapExplanations: (modelId: string, sampleSize: number = 150) =>
    request<ShapExplanationResponse>("/api/v1/explainability/shap", {
      method: "POST",
      body: JSON.stringify({ model_id: modelId, sample_size: sampleSize }),
    }),

  // Reports
  getReports: () => request<{ reports: Array<{ filename: string; size_bytes: number; modified_time: number; type: string; download_url: string }> }>("/api/v1/reports"),
};

