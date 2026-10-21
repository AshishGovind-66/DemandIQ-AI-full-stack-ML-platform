import pytest
import pandas as pd
import numpy as np
from backend.app.forecasting.registry import ModelRegistry
from backend.app.forecasting.baseline_models import NaiveForecaster, SeasonalNaiveForecaster
from backend.app.forecasting.ml_models import LinearRegressionForecaster, XGBoostForecaster, LightGBMForecaster
from backend.app.forecasting.trainer import ForecastTrainer
from backend.app.forecasting.predictor import ForecastPredictor

def test_model_registry_discovery():
    models = ModelRegistry.list_models()
    assert "naive" in models
    assert "seasonal_naive" in models
    assert "xgboost" in models
    assert "lightgbm" in models

def test_trainer_pipeline_on_sample(sample_sales_df):
    trainer = ForecastTrainer(
        candidate_models=["naive", "seasonal_naive", "linear_regression", "lightgbm"],
        validation_days=7,
        test_days=7
    )
    res = trainer.train_and_evaluate(
        df=sample_sales_df,
        dataset_id="test-dataset-id"
    )
    assert "trained_models" in res
    assert len(res["trained_models"]) == 4
    assert res["best_model_name"] is not None
    # Best model must have is_best == True
    best_recs = [m for m in res["trained_models"] if m["is_best"]]
    assert len(best_recs) == 1

def test_forecast_predictor_multistep(sample_sales_df):
    # First train a model to get an artifact
    trainer = ForecastTrainer(
        candidate_models=["naive", "lightgbm"],
        validation_days=7,
        test_days=7
    )
    res = trainer.train_and_evaluate(df=sample_sales_df, dataset_id="test-dataset-id")
    best_artifact = [m["artifact_path"] for m in res["trained_models"] if m["is_best"]][0]

    # Generate 14-day forward forecast
    fc = ForecastPredictor.generate_forecast(
        artifact_path=best_artifact,
        historical_df=sample_sales_df,
        horizon_days=14,
        confidence_level=0.95
    )
    assert fc["horizon_days"] == 14
    assert fc["total_forecasted_demand"] > 0
    assert len(fc["forecast_points_sample"]) > 0
    
    first_pt = fc["forecast_points_sample"][0]
    assert first_pt["lower_bound"] <= first_pt["predicted_demand"] <= first_pt["upper_bound"]

