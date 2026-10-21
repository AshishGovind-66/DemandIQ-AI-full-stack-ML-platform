import os
import uuid
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import get_db
from backend.app.models.db_models import DatasetModel, TrainedModelRecord, ForecastRunModel
from backend.app.schemas.forecast import ForecastRequest, ForecastResponse, ForecastPoint
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.forecasting.predictor import ForecastPredictor
from backend.app.reporting.export_service import ExportService

router = APIRouter()

@router.post("/generate", response_model=ForecastResponse)
def generate_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db)
):
    """Generates future multi-step demand predictions with prediction intervals."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == request.dataset_id).first()
    if not dataset or not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="Dataset not found or data file missing.")

    # Find model: specific or best
    if request.model_id:
        model_rec = db.query(TrainedModelRecord).filter(TrainedModelRecord.id == request.model_id).first()
    else:
        # Default to best model for this dataset
        model_rec = db.query(TrainedModelRecord).filter(
            TrainedModelRecord.dataset_id == request.dataset_id,
            TrainedModelRecord.is_best == True
        ).first()
        if not model_rec:
            # Fallback to any trained model
            model_rec = db.query(TrainedModelRecord).filter(
                TrainedModelRecord.dataset_id == request.dataset_id
            ).first()

    if not model_rec or not os.path.exists(model_rec.artifact_path):
        raise HTTPException(
            status_code=400,
            detail="No trained model artifact available. Please train models first under the Model Training tab."
        )

    # Load canonical dataset
    raw_df = pd.read_csv(dataset.file_path)
    if "date" in raw_df.columns and "sales" in raw_df.columns:
        canonical_df = raw_df
    else:
        mapping = ColumnMappingConfig(**(dataset.column_mapping or {}))
        canonical_df = ColumnMapper.apply_mapping(raw_df, mapping)

    try:
        forecast_result = ForecastPredictor.generate_forecast(
            artifact_path=model_rec.artifact_path,
            historical_df=canonical_df,
            horizon_days=request.horizon_days,
            confidence_level=request.confidence_level,
            product_ids=request.product_ids,
            store_ids=request.store_ids
        )
    except Exception as e:
        logger.error(f"Forecast generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

    # Export to CSV
    csv_path = ExportService.export_dataframe_to_csv(
        forecast_result["forecast_df"],
        prefix=f"forecast_{dataset.id[:6]}"
    )

    forecast_run_id = str(uuid.uuid4())
    run_record = ForecastRunModel(
        id=forecast_run_id,
        dataset_id=dataset.id,
        model_id=model_rec.id,
        horizon_days=request.horizon_days,
        start_date=forecast_result["start_date"],
        end_date=forecast_result["end_date"],
        summary_metrics={
            "total_demand": forecast_result["total_forecasted_demand"],
            "average_daily_demand": forecast_result["average_daily_demand"]
        },
        forecast_points_sample=forecast_result["forecast_points_sample"],
        results_csv_path=str(csv_path)
    )
    db.add(run_record)
    db.commit()

    sample_points = [ForecastPoint(**pt) for pt in forecast_result["forecast_points_sample"]]

    return ForecastResponse(
        forecast_run_id=forecast_run_id,
        model_id=model_rec.id,
        model_name=model_rec.model_name,
        horizon_days=request.horizon_days,
        confidence_level=request.confidence_level,
        start_date=forecast_result["start_date"],
        end_date=forecast_result["end_date"],
        total_forecasted_demand=forecast_result["total_forecasted_demand"],
        average_daily_demand=forecast_result["average_daily_demand"],
        points_count=forecast_result["points_count"],
        forecast_points_sample=sample_points,
        historical_comparison=forecast_result["historical_comparison"]
    )

@router.get("/{forecast_run_id}")
def get_forecast_run(forecast_run_id: str, db: Session = Depends(get_db)):
    """Retrieves previous forecast run results."""
    run = db.query(ForecastRunModel).filter(ForecastRunModel.id == forecast_run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Forecast run not found")
    return {
        "id": run.id,
        "dataset_id": run.dataset_id,
        "model_id": run.model_id,
        "horizon_days": run.horizon_days,
        "start_date": run.start_date,
        "end_date": run.end_date,
        "summary": run.summary_metrics,
        "points_sample": run.forecast_points_sample,
        "csv_path": run.results_csv_path,
        "created_at": run.created_at.isoformat() if run.created_at else ""
    }

