import os
import uuid
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import get_db
from backend.app.models.db_models import DatasetModel, ForecastRunModel, InventoryPlanModel
from backend.app.schemas.inventory import (
    InventoryOptimizationRequest,
    InventoryOptimizationSummary,
    ItemInventoryRecommendation
)
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.inventory.optimization_engine import InventoryOptimizationEngine
from backend.app.reporting.export_service import ExportService

router = APIRouter()

@router.post("/optimize", response_model=InventoryOptimizationSummary)
def optimize_inventory(
    request: InventoryOptimizationRequest,
    db: Session = Depends(get_db)
):
    """Calculates optimal safety stock, reorder point, order quantity and stockout risks."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == request.dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found or data file missing.")

    # Load canonical dataset
    raw_df = pd.read_csv(dataset.file_path)
    if "date" in raw_df.columns and "sales" in raw_df.columns:
        canonical_df = raw_df
    else:
        mapping = ColumnMappingConfig(**(dataset.column_mapping or {}))
        canonical_df = ColumnMapper.apply_mapping(raw_df, mapping)

    # Load forecast if available
    forecast_df = None
    if request.forecast_run_id:
        forecast_run = db.query(ForecastRunModel).filter(ForecastRunModel.id == request.forecast_run_id).first()
        if forecast_run and forecast_run.results_csv_path and os.path.exists(forecast_run.results_csv_path):
            try:
                forecast_df = pd.read_csv(forecast_run.results_csv_path)
            except Exception as e:
                logger.warning(f"Could not load forecast CSV: {e}")

    try:
        summary = InventoryOptimizationEngine.optimize(
            historical_df=canonical_df,
            request=request,
            forecast_df=forecast_df
        )
    except Exception as e:
        logger.error(f"Inventory optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Inventory optimization failed: {str(e)}")

    # Export to CSV
    recs_dicts = [rec.dict() for rec in summary.recommendations]
    csv_path = ExportService.generate_inventory_csv(recs_dicts)

    # Save to DB
    plan_record = InventoryPlanModel(
        id=summary.plan_id,
        dataset_id=dataset.id,
        forecast_run_id=request.forecast_run_id,
        service_level=request.service_level,
        lead_time_days=request.lead_time_days,
        parameters=request.dict(),
        summary_metrics={
            "total_products": summary.total_products_analyzed,
            "stockout_risk_count": summary.items_at_stockout_risk,
            "excess_stock_count": summary.items_with_excess_stock,
            "total_reorder_units": summary.total_suggested_reorder_units,
            "total_reorder_value": summary.total_estimated_reorder_value,
            "total_holding_cost": summary.total_holding_cost_estimate
        },
        recommendations_sample=recs_dicts[:100],
        results_csv_path=str(csv_path)
    )
    db.add(plan_record)
    db.commit()

    return summary

@router.get("/{plan_id}")
def get_inventory_plan(plan_id: str, db: Session = Depends(get_db)):
    """Retrieves previous inventory plan details."""
    plan = db.query(InventoryPlanModel).filter(InventoryPlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Inventory plan not found")
    return {
        "id": plan.id,
        "dataset_id": plan.dataset_id,
        "service_level": plan.service_level,
        "lead_time_days": plan.lead_time_days,
        "summary": plan.summary_metrics,
        "recommendations": plan.recommendations_sample,
        "csv_path": plan.results_csv_path,
        "created_at": plan.created_at.isoformat() if plan.created_at else ""
    }

