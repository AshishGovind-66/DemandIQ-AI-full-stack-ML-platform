import threading
import uuid
import datetime
from typing import Dict, Any, Optional
from backend.app.core.logging import logger
from backend.app.database.session import SessionLocal
from backend.app.models.db_models import TrainingJobModel, TrainedModelRecord

class JobManager:
    """Manages asynchronous background training jobs and status tracking."""

    _jobs: Dict[str, Dict[str, Any]] = {}
    _lock = threading.Lock()

    @classmethod
    def create_job(cls, dataset_id: str, models: list[str], horizon_days: int) -> str:
        job_id = str(uuid.uuid4())
        job_data = {
            "job_id": job_id,
            "dataset_id": dataset_id,
            "status": "QUEUED",
            "progress_pct": 0,
            "current_step": "Job queued",
            "models_to_train": models,
            "horizon_days": horizon_days,
            "error_message": None,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "completed_at": None,
            "models": [],
            "best_model_name": None
        }
        with cls._lock:
            cls._jobs[job_id] = job_data

        # Also persist to database
        db = SessionLocal()
        try:
            db_job = TrainingJobModel(
                id=job_id,
                dataset_id=dataset_id,
                status="QUEUED",
                models_to_train=models,
                horizon_days=horizon_days,
                current_step="Job queued",
                progress_pct=0,
                config_json={"models": models, "horizon_days": horizon_days}
            )
            db.add(db_job)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to persist job to db: {e}")
            db.rollback()
        finally:
            db.close()

        return job_id

    @classmethod
    def update_job(
        cls,
        job_id: str,
        status: Optional[str] = None,
        progress_pct: Optional[int] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None,
        models: Optional[list] = None,
        best_model_name: Optional[str] = None
    ) -> None:
        with cls._lock:
            if job_id not in cls._jobs:
                return
            job = cls._jobs[job_id]
            if status:
                job["status"] = status
            if progress_pct is not None:
                job["progress_pct"] = progress_pct
            if current_step:
                job["current_step"] = current_step
            if error_message:
                job["error_message"] = error_message
            if models is not None:
                job["models"] = models
            if best_model_name:
                job["best_model_name"] = best_model_name
            if status in ["COMPLETED", "FAILED"]:
                job["completed_at"] = datetime.datetime.utcnow().isoformat()

        # Update database record
        db = SessionLocal()
        try:
            db_job = db.query(TrainingJobModel).filter(TrainingJobModel.id == job_id).first()
            if db_job:
                if status:
                    db_job.status = status
                if progress_pct is not None:
                    db_job.progress_pct = progress_pct
                if current_step:
                    db_job.current_step = current_step
                if error_message:
                    db_job.error_message = error_message
                if status in ["COMPLETED", "FAILED"]:
                    db_job.completed_at = datetime.datetime.utcnow()
                db.commit()
        except Exception as e:
            logger.error(f"Failed to update job in db: {e}")
            db.rollback()
        finally:
            db.close()

    @classmethod
    def get_job(cls, job_id: str) -> Optional[Dict[str, Any]]:
        with cls._lock:
            if job_id in cls._jobs:
                return cls._jobs[job_id]

        # Check database fallback
        db = SessionLocal()
        try:
            db_job = db.query(TrainingJobModel).filter(TrainingJobModel.id == job_id).first()
            if db_job:
                models_records = db.query(TrainedModelRecord).filter(TrainedModelRecord.job_id == job_id).all()
                model_summaries = [
                    {
                        "id": m.id,
                        "model_name": m.model_name,
                        "model_type": m.model_type,
                        "metrics": m.metrics,
                        "is_best": m.is_best,
                        "parameters": m.parameters,
                        "created_at": m.created_at.isoformat() if m.created_at else ""
                    }
                    for m in models_records
                ]
                best_m = next((m.model_name for m in models_records if m.is_best), None)
                return {
                    "job_id": db_job.id,
                    "dataset_id": db_job.dataset_id,
                    "status": db_job.status,
                    "progress_pct": db_job.progress_pct,
                    "current_step": db_job.current_step,
                    "error_message": db_job.error_message,
                    "created_at": db_job.created_at.isoformat() if db_job.created_at else "",
                    "completed_at": db_job.completed_at.isoformat() if db_job.completed_at else None,
                    "models": model_summaries,
                    "best_model_name": best_m
                }
        finally:
            db.close()

        return None

