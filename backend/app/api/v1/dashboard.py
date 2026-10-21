from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.database.session import get_db
from backend.app.models.db_models import (
    DatasetModel,
    TrainingJobModel,
    TrainedModelRecord,
    ForecastRunModel,
    InventoryPlanModel
)
from backend.app.api.v1.datasets import seed_sample_dataset_if_empty

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Computes real summary metrics across all active datasets, models, forecasts, and inventory plans.
    Does NOT return fabricated numbers. Returns zero/empty indicators when unpopulated.
    """
    seed_sample_dataset_if_empty(db)

    # 1. Datasets count and products count
    datasets = db.query(DatasetModel).filter(DatasetModel.is_active == True).all()
    total_datasets = len(datasets)
    
    total_products = 0
    total_historical_sales = 0.0
    for d in datasets:
        metrics = d.summary_metrics or {}
        total_products += metrics.get("products", metrics.get("items_count", 0))
        total_historical_sales += metrics.get("total_sales", 0.0)

    # 2. Latest Forecast Metrics
    latest_forecast = db.query(ForecastRunModel).order_by(desc(ForecastRunModel.created_at)).first()
    forecasted_demand = 0.0
    forecast_horizon = 0
    forecast_model_name = None
    if latest_forecast and latest_forecast.summary_metrics:
        forecasted_demand = latest_forecast.summary_metrics.get("total_demand", 0.0)
        forecast_horizon = latest_forecast.horizon_days
        if latest_forecast.model:
            forecast_model_name = latest_forecast.model.model_name

    # 3. Latest Inventory Plan Metrics
    latest_inv = db.query(InventoryPlanModel).order_by(desc(InventoryPlanModel.created_at)).first()
    stockout_count = 0
    excess_count = 0
    total_reorder_qty = 0
    total_reorder_val = 0.0
    if latest_inv and latest_inv.summary_metrics:
        sm = latest_inv.summary_metrics
        stockout_count = sm.get("stockout_risk_count", 0)
        excess_count = sm.get("excess_stock_count", 0)
        total_reorder_qty = sm.get("total_reorder_units", 0)
        total_reorder_val = sm.get("total_reorder_value", 0.0)

    # 4. Best Model Metrics
    best_model = db.query(TrainedModelRecord).filter(TrainedModelRecord.is_best == True).order_by(desc(TrainedModelRecord.created_at)).first()
    if not best_model:
        best_model = db.query(TrainedModelRecord).order_by(desc(TrainedModelRecord.created_at)).first()

    best_model_summary = None
    if best_model:
        best_model_summary = {
            "id": best_model.id,
            "model_name": best_model.model_name,
            "metrics": best_model.metrics,
            "created_at": best_model.created_at.isoformat() if best_model.created_at else ""
        }

    # 5. Recent Training Jobs
    recent_jobs = db.query(TrainingJobModel).order_by(desc(TrainingJobModel.created_at)).limit(5).all()
    jobs_summary = [
        {
            "id": j.id,
            "dataset_id": j.dataset_id,
            "status": j.status,
            "progress_pct": j.progress_pct,
            "current_step": j.current_step,
            "models_to_train": j.models_to_train,
            "created_at": j.created_at.isoformat() if j.created_at else ""
        }
        for j in recent_jobs
    ]

    return {
        "has_data": total_datasets > 0,
        "total_datasets": total_datasets,
        "total_products": total_products,
        "total_historical_sales": round(total_historical_sales, 1),
        "latest_forecast": {
            "has_forecast": latest_forecast is not None,
            "total_demand": round(forecasted_demand, 1),
            "horizon_days": forecast_horizon,
            "model_name": forecast_model_name,
            "created_at": latest_forecast.created_at.isoformat() if latest_forecast and latest_forecast.created_at else None
        },
        "latest_inventory": {
            "has_inventory_plan": latest_inv is not None,
            "stockout_risk_count": stockout_count,
            "excess_stock_count": excess_count,
            "total_suggested_reorder_units": total_reorder_qty,
            "total_estimated_reorder_value": round(total_reorder_val, 2),
            "created_at": latest_inv.created_at.isoformat() if latest_inv and latest_inv.created_at else None
        },
        "best_model": best_model_summary,
        "recent_jobs": jobs_summary
    }

