import threading
import os
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.database.session import get_db, SessionLocal
from backend.app.models.db_models import DatasetModel, TrainingJobModel, TrainedModelRecord
from backend.app.schemas.training import (
    TrainingRequest,
    TrainingJobStatusResponse,
    TrainedModelSummary,
    ModelMetrics
)
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.forecasting.trainer import ForecastTrainer
from backend.app.services.job_manager import JobManager

router = APIRouter()

def run_training_background_task(job_id: str, dataset_id: str, request_dict: dict):
    """Background worker function executing the training pipeline."""
    db = SessionLocal()
    try:
        JobManager.update_job(job_id, status="RUNNING", progress_pct=10, current_step="Loading and validating data")
        
        dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
        if not dataset or not os.path.exists(dataset.file_path):
            JobManager.update_job(job_id, status="FAILED", error_message="Dataset file missing")
            return

        raw_df = pd.read_csv(dataset.file_path)
        if "date" in raw_df.columns and "sales" in raw_df.columns:
            canonical_df = raw_df
        else:
            mapping = ColumnMappingConfig(**(dataset.column_mapping or {}))
            canonical_df = ColumnMapper.apply_mapping(raw_df, mapping)

        # Product filter if requested
        if request_dict.get("product_ids"):
            canonical_df = canonical_df[canonical_df["product_id"].isin(request_dict["product_ids"])]
        if request_dict.get("store_ids"):
            canonical_df = canonical_df[canonical_df["store_id"].isin(request_dict["store_ids"])]

        JobManager.update_job(job_id, progress_pct=30, current_step="Splitting time-series & engineering features")

        trainer = ForecastTrainer(
            candidate_models=request_dict.get("models"),
            validation_days=request_dict.get("validation_days", 14),
            test_days=request_dict.get("horizon_days", 14),
            max_rows=request_dict.get("max_training_rows", 100000)
        )

        JobManager.update_job(job_id, progress_pct=50, current_step="Training models & evaluating on validation split")

        training_results = trainer.train_and_evaluate(
            df=canonical_df,
            dataset_id=dataset_id,
            job_id=job_id
        )

        JobManager.update_job(job_id, progress_pct=85, current_step="Persisting model artifacts and metrics")

        # Save model records to DB
        model_summaries = []
        for m in training_results["trained_models"]:
            db_model = TrainedModelRecord(
                id=m["id"],
                job_id=job_id,
                dataset_id=dataset_id,
                model_name=m["model_name"],
                model_type=m["model_type"],
                parameters=m["parameters"],
                metrics=m["metrics"],
                artifact_path=m["artifact_path"],
                feature_importance=m["feature_importance"],
                is_best=m["is_best"]
            )
            db.add(db_model)
            model_summaries.append({
                "id": m["id"],
                "model_name": m["model_name"],
                "model_type": m["model_type"],
                "metrics": m["metrics"],
                "is_best": m["is_best"],
                "parameters": m["parameters"],
                "created_at": db_model.created_at.isoformat() if db_model.created_at else ""
            })

        db.commit()

        JobManager.update_job(
            job_id,
            status="COMPLETED",
            progress_pct=100,
            current_step="Training complete",
            models=model_summaries,
            best_model_name=training_results["best_model_name"]
        )
        logger.info(f"Training job {job_id} completed successfully.")

    except Exception as e:
        logger.error(f"Training job {job_id} failed: {str(e)}", exc_info=True)
        JobManager.update_job(job_id, status="FAILED", error_message=str(e), current_step="Error during training")
    finally:
        db.close()

@router.post("/datasets/{dataset_id}/train")
def start_model_training(
    dataset_id: str,
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Initiates an asynchronous model training and comparison job."""
    dataset = db.query(DatasetModel).filter(DatasetModel.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    job_id = JobManager.create_job(
        dataset_id=dataset_id,
        models=request.models,
        horizon_days=request.horizon_days
    )

    background_tasks.add_task(
        run_training_background_task,
        job_id=job_id,
        dataset_id=dataset_id,
        request_dict=request.dict()
    )

    return {
        "job_id": job_id,
        "dataset_id": dataset_id,
        "status": "QUEUED",
        "message": f"Training initiated for {len(request.models)} models. Track progress via /jobs/{job_id}"
    }

@router.get("/jobs/{job_id}", response_model=TrainingJobStatusResponse)
def get_job_status(job_id: str):
    """Retrieves current execution progress and model metrics for a training job."""
    job_info = JobManager.get_job(job_id)
    if not job_info:
        raise HTTPException(status_code=404, detail="Training job not found")

    models_list = [
        TrainedModelSummary(
            id=m["id"],
            model_name=m["model_name"],
            model_type=m["model_type"],
            metrics=ModelMetrics(**m["metrics"]),
            is_best=m.get("is_best", False),
            parameters=m.get("parameters", {}),
            created_at=m.get("created_at", "")
        )
        for m in job_info.get("models", [])
    ]

    return TrainingJobStatusResponse(
        job_id=job_info["job_id"],
        dataset_id=job_info["dataset_id"],
        status=job_info["status"],
        progress_pct=job_info["progress_pct"],
        current_step=job_info["current_step"],
        error_message=job_info.get("error_message"),
        created_at=job_info["created_at"],
        completed_at=job_info.get("completed_at"),
        models=models_list,
        best_model_name=job_info.get("best_model_name")
    )

@router.get("/models/comparison/{dataset_id}")
def get_model_comparison(dataset_id: str, db: Session = Depends(get_db)):
    """Returns leaderboard comparison of all models trained on this dataset."""
    models = db.query(TrainedModelRecord).filter(TrainedModelRecord.dataset_id == dataset_id).order_by(TrainedModelRecord.created_at.desc()).all()
    if not models:
        return {"dataset_id": dataset_id, "models": []}

    return {
        "dataset_id": dataset_id,
        "models": [
            {
                "id": m.id,
                "model_name": m.model_name,
                "model_type": m.model_type,
                "metrics": m.metrics,
                "is_best": m.is_best,
                "parameters": m.parameters,
                "created_at": m.created_at.isoformat() if m.created_at else ""
            }
            for m in models
        ]
    }

@router.get("/models/{model_id}")
def get_model_detail(model_id: str, db: Session = Depends(get_db)):
    """Returns details and feature importance for a single trained model."""
    m = db.query(TrainedModelRecord).filter(TrainedModelRecord.id == model_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Model record not found")
    return {
        "id": m.id,
        "job_id": m.job_id,
        "dataset_id": m.dataset_id,
        "model_name": m.model_name,
        "model_type": m.model_type,
        "metrics": m.metrics,
        "is_best": m.is_best,
        "parameters": m.parameters,
        "feature_importance": m.feature_importance,
        "created_at": m.created_at.isoformat() if m.created_at else ""
    }

