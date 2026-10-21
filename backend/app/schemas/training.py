from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TrainingRequest(BaseModel):
    models: List[str] = Field(
        default=["naive", "seasonal_naive", "linear_regression", "xgboost", "lightgbm"],
        description="List of model keys to train"
    )
    horizon_days: int = Field(default=14, ge=1, le=90, description="Forecast horizon in days")
    validation_days: int = Field(default=14, ge=7, le=90, description="Validation window for hyperparameter & model selection")
    product_ids: Optional[List[str]] = Field(default=None, description="Optional list of products to subset")
    store_ids: Optional[List[str]] = Field(default=None, description="Optional list of stores to subset")
    max_training_rows: Optional[int] = Field(default=100000, description="Safety limit on training rows")

class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    wape: float
    bias: float
    test_rows: int

class TrainedModelSummary(BaseModel):
    id: str
    model_name: str
    model_type: str
    metrics: ModelMetrics
    is_best: bool
    parameters: Dict[str, Any] = {}
    created_at: str

class TrainingJobStatusResponse(BaseModel):
    job_id: str
    dataset_id: str
    status: str
    progress_pct: int
    current_step: str
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    models: List[TrainedModelSummary] = []
    best_model_name: Optional[str] = None

