import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_type = Column(String(50), default="csv")  # csv, m5_walmart, etc.
    file_size_bytes = Column(Integer, default=0)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_json = Column(JSON, default=list)
    column_mapping = Column(JSON, default=dict)
    summary_metrics = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    training_jobs = relationship("TrainingJobModel", back_populates="dataset", cascade="all, delete-orphan")
    trained_models = relationship("TrainedModelRecord", back_populates="dataset", cascade="all, delete-orphan")
    forecast_runs = relationship("ForecastRunModel", back_populates="dataset", cascade="all, delete-orphan")


class TrainingJobModel(Base):
    __tablename__ = "training_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    status = Column(String(50), default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED
    models_to_train = Column(JSON, default=list)
    horizon_days = Column(Integer, default=14)
    current_step = Column(String(255), default="Initializing")
    progress_pct = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    config_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("DatasetModel", back_populates="training_jobs")
    models = relationship("TrainedModelRecord", back_populates="job", cascade="all, delete-orphan")


class TrainedModelRecord(Base):
    __tablename__ = "trained_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    job_id = Column(String(36), ForeignKey("training_jobs.id"), nullable=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    model_name = Column(String(100), nullable=False)  # naive, xgboost, lightgbm, etc.
    model_type = Column(String(50), nullable=False)  # baseline, ml
    parameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)  # mae, rmse, wape, bias
    artifact_path = Column(String(1024), nullable=True)
    feature_importance = Column(JSON, default=dict)
    is_best = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    job = relationship("TrainingJobModel", back_populates="models")
    dataset = relationship("DatasetModel", back_populates="trained_models")
    forecasts = relationship("ForecastRunModel", back_populates="model")


class ForecastRunModel(Base):
    __tablename__ = "forecast_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    model_id = Column(String(36), ForeignKey("trained_models.id"), nullable=True)
    horizon_days = Column(Integer, default=14)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    summary_metrics = Column(JSON, default=dict)
    forecast_points_sample = Column(JSON, default=list)  # Top sample for UI
    results_csv_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    dataset = relationship("DatasetModel", back_populates="forecast_runs")
    model = relationship("TrainedModelRecord", back_populates="forecasts")
    inventory_plans = relationship("InventoryPlanModel", back_populates="forecast_run")


class InventoryPlanModel(Base):
    __tablename__ = "inventory_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    forecast_run_id = Column(String(36), ForeignKey("forecast_runs.id"), nullable=True)
    dataset_id = Column(String(36), ForeignKey("datasets.id"), nullable=False)
    service_level = Column(Float, default=0.95)
    lead_time_days = Column(Integer, default=7)
    parameters = Column(JSON, default=dict)
    summary_metrics = Column(JSON, default=dict)
    recommendations_sample = Column(JSON, default=list)
    results_csv_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    forecast_run = relationship("ForecastRunModel", back_populates="inventory_plans")


class ReportModel(Base):
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # profile, forecast, inventory, comparison
    dataset_id = Column(String(36), nullable=True)
    summary_data = Column(JSON, default=dict)
    file_path = Column(String(1024), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

