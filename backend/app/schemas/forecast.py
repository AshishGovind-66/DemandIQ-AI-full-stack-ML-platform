from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ForecastRequest(BaseModel):
    dataset_id: str
    model_id: Optional[str] = Field(default=None, description="Trained model ID; uses best model if omitted")
    horizon_days: int = Field(default=14, ge=1, le=90, description="Forecast horizon in days")
    confidence_level: float = Field(default=0.95, ge=0.50, le=0.99, description="Confidence interval level")
    product_ids: Optional[List[str]] = Field(default=None, description="Optional product filter")
    store_ids: Optional[List[str]] = Field(default=None, description="Optional store filter")

class ForecastPoint(BaseModel):
    date: str
    product_id: str
    store_id: Optional[str] = None
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    actual_demand: Optional[float] = None

class ForecastResponse(BaseModel):
    forecast_run_id: str
    model_id: str
    model_name: str
    horizon_days: int
    confidence_level: float
    start_date: str
    end_date: str
    total_forecasted_demand: float
    average_daily_demand: float
    points_count: int
    forecast_points_sample: List[ForecastPoint] = []
    historical_comparison: List[Dict[str, Any]] = []

