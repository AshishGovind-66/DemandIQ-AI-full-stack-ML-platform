// ==========================================
// DemandIQ AI - TypeScript Interfaces
// ==========================================

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  database: string;
  walmart_m5_available: boolean;
  available_models: string[];
  system_info: {
    python_version: string;
    platform: string;
    m5_files: Record<string, { available: boolean; path: string | null; size_mb: number }>;
  };
}

export interface Dataset {
  id: string;
  name: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  columns: string[];
  column_mapping: Record<string, string>;
  created_at: string;
}

export interface ValidationIssue {
  severity: "ERROR" | "WARNING" | "INFO";
  field?: string;
  message: string;
}

export interface ValidationResult {
  is_valid: boolean;
  issues: ValidationIssue[];
  row_count: number;
  column_count: number;
  detected_columns: string[];
  detected_types: Record<string, string>;
  missing_dates_count: number;
  negative_values_count: number;
  duplicate_rows_count: number;
}

export interface ColumnMappingConfig {
  date_col: string;
  target_col: string;
  product_id_col?: string;
  store_id_col?: string;
  category_col?: string;
  price_col?: string;
  promo_col?: string;
}

export interface DataProfilingReport {
  dataset_id: string;
  dataset_name: string;
  total_rows: number;
  total_columns: number;
  start_date: string | null;
  end_date: string | null;
  total_duration_days: number | null;
  unique_products_count: number;
  unique_stores_count: number;
  total_sales_volume: number;
  mean_daily_sales: number;
  median_daily_sales: number;
  std_daily_sales: number;
  zero_sales_percentage: number;
  missing_values_by_column: Record<string, number>;
  duplicate_rows: number;
  top_products: Array<{ product_id: string; total_sales: number }>;
  top_stores: Array<{ store_id: string; total_sales: number }>;
  category_breakdown: Array<{ category: string; total_sales: number }>;
  daily_trend_sample: Array<{ date: string; sales: number }>;
  day_of_week_pattern: Array<{ day: string; day_full: string; avg_sales: number }>;
  monthly_pattern: Array<{ month: string; avg_sales: number }>;
}

export interface ModelMetrics {
  mae: number;
  rmse: number;
  wape: number;
  bias: number;
  test_rows: number;
}

export interface TrainedModel {
  id: string;
  model_name: string;
  model_type: string;
  metrics: ModelMetrics;
  is_best: boolean;
  parameters: Record<string, any>;
  feature_importance?: Record<string, number>;
  created_at: string;
}

export interface TrainingJob {
  job_id: string;
  dataset_id: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";
  progress_pct: number;
  current_step: string;
  error_message?: string | null;
  created_at: string;
  completed_at?: string | null;
  models: TrainedModel[];
  best_model_name?: string | null;
}

export interface ForecastPoint {
  date: string;
  product_id: string;
  store_id?: string;
  predicted_demand: number;
  lower_bound: number;
  upper_bound: number;
  actual_demand?: number | null;
}

export interface ForecastResponse {
  forecast_run_id: string;
  model_id: string;
  model_name: string;
  horizon_days: number;
  confidence_level: number;
  start_date: string;
  end_date: string;
  total_forecasted_demand: number;
  average_daily_demand: number;
  points_count: number;
  forecast_points_sample: ForecastPoint[];
  historical_comparison: Array<{ date: string; actual_sales: number }>;
}

export interface ItemInventoryRecommendation {
  product_id: string;
  store_id?: string;
  category?: string;
  unit_price: number;
  daily_demand_mean: number;
  daily_demand_std: number;
  lead_time_days: number;
  service_level: number;
  z_score: number;
  expected_lead_time_demand: number;
  safety_stock: number;
  reorder_point: number;
  current_on_hand: number;
  on_order: number;
  inventory_position: number;
  target_stock: number;
  suggested_order_qty: number;
  stockout_risk: boolean;
  excess_stock_risk: boolean;
  days_of_supply_remaining: number;
  estimated_holding_cost: number;
}

export interface InventoryOptimizationSummary {
  plan_id: string;
  dataset_id: string;
  lead_time_days: number;
  service_level: number;
  total_products_analyzed: number;
  items_at_stockout_risk: number;
  items_with_excess_stock: number;
  total_suggested_reorder_units: number;
  total_estimated_reorder_value: number;
  total_holding_cost_estimate: number;
  recommendations: ItemInventoryRecommendation[];
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
  description: string;
}

export interface ShapExplanationResponse {
  model_id: string;
  model_name: string;
  is_supported: boolean;
  summary_message: string;
  global_feature_importance: FeatureImportanceItem[];
  top_drivers_summary: string[];
}

export interface DashboardSummary {
  has_data: boolean;
  total_datasets: number;
  total_products: number;
  total_historical_sales: number;
  latest_forecast: {
    has_forecast: boolean;
    total_demand: number;
    horizon_days: number;
    model_name?: string | null;
    created_at?: string | null;
  };
  latest_inventory: {
    has_inventory_plan: boolean;
    stockout_risk_count: number;
    excess_stock_count: number;
    total_suggested_reorder_units: number;
    total_estimated_reorder_value: number;
    created_at?: string | null;
  };
  best_model?: {
    id: string;
    model_name: string;
    metrics: ModelMetrics;
    created_at: string;
  } | null;
  recent_jobs: Array<{
    id: string;
    dataset_id: string;
    status: string;
    progress_pct: number;
    current_step: string;
    models_to_train: string[];
    created_at: string;
  }>;
}

