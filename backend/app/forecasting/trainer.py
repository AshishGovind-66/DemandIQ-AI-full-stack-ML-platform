import os
import uuid
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import joblib

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.forecasting.registry import ModelRegistry
from backend.app.preprocessing.feature_engineering import FeatureEngineer
from backend.app.utils.time_series import chronological_split
from backend.app.utils.metrics import compute_all_metrics
from backend.app.utils.exceptions import ModelTrainingError

class ForecastTrainer:
    """
    Orchestrates leakage-free chronological training, model selection on validation,
    and out-of-sample test evaluation.
    """

    def __init__(
        self,
        candidate_models: Optional[List[str]] = None,
        validation_days: int = 14,
        test_days: int = 14,
        max_rows: int = 100000
    ):
        if not candidate_models:
            candidate_models = ["naive", "seasonal_naive", "linear_regression", "xgboost", "lightgbm"]
        self.candidate_models = candidate_models
        self.validation_days = validation_days
        self.test_days = test_days
        self.max_rows = max_rows

    def train_and_evaluate(
        self,
        df: pd.DataFrame,
        dataset_id: str,
        job_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete training and model evaluation pipeline.
        """
        logger.info(f"Starting model training on {len(df)} rows across {df['product_id'].nunique()} products.")
        
        # 1. Limit rows if exceeds max for safety
        if len(df) > self.max_rows:
            logger.warning(f"Dataset has {len(df)} rows, taking most recent {self.max_rows} rows.")
            df = df.sort_values(by="date").tail(self.max_rows).reset_index(drop=True)

        # 2. Chronological split: train, val, test
        train_df, val_df, test_df = chronological_split(
            df=df,
            date_col="date",
            validation_days=self.validation_days,
            test_days=self.test_days
        )
        logger.info(f"Splits created: Train={len(train_df)} rows, Val={len(val_df)} rows, Test={len(test_df)} rows.")

        # 3. Fit feature engineering pipeline strictly on train data
        fe = FeatureEngineer()
        train_feat_df, feature_names = fe.fit_transform(train_df)
        val_feat_df = fe.transform(val_df)
        test_feat_df = fe.transform(test_df)

        X_train, y_train = fe.get_features_and_target(train_feat_df)
        X_val, y_val = fe.get_features_and_target(val_feat_df)
        X_test, y_test = fe.get_features_and_target(test_feat_df)

        results = []
        best_model_name = None
        best_val_wape = float("inf")
        best_forecaster_obj = None

        # 4. Train and evaluate each candidate model
        for model_name in self.candidate_models:
            try:
                logger.info(f"Training model: {model_name}...")
                forecaster = ModelRegistry.get(model_name)
                forecaster.fit(X_train, y_train)

                # Predictions on Validation
                val_preds = forecaster.predict(X_val)
                val_metrics = compute_all_metrics(y_val, val_preds)

                # Predictions on Test
                test_preds = forecaster.predict(X_test)
                test_metrics = compute_all_metrics(y_test, test_preds)

                # Calculate residual standard deviation for prediction intervals
                residuals = y_val - val_preds
                forecaster.set_residual_std(float(np.std(residuals)))

                # Save trained artifact
                model_artifact_id = str(uuid.uuid4())
                artifact_filename = f"{model_artifact_id}_{model_name}.joblib"
                artifact_path = settings.MODELS_DIR / artifact_filename
                
                # Bundle model + fitted feature engineer + metadata
                artifact_bundle = {
                    "model_id": model_artifact_id,
                    "model_name": model_name,
                    "model_type": forecaster.model_type,
                    "forecaster": forecaster,
                    "feature_engineer": fe,
                    "feature_names": feature_names,
                    "val_metrics": val_metrics,
                    "test_metrics": test_metrics,
                    "parameters": forecaster.get_params(),
                    "dataset_id": dataset_id,
                    "validation_days": self.validation_days,
                    "test_days": self.test_days
                }
                joblib.dump(artifact_bundle, artifact_path)

                feat_imp = forecaster.get_feature_importance()

                model_record = {
                    "id": model_artifact_id,
                    "model_name": model_name,
                    "model_type": forecaster.model_type,
                    "val_metrics": val_metrics,
                    "test_metrics": test_metrics,
                    "metrics": test_metrics,  # Default display metrics
                    "parameters": forecaster.get_params(),
                    "feature_importance": feat_imp,
                    "artifact_path": str(artifact_path),
                    "is_best": False
                }
                results.append(model_record)

                # Model selection on VALIDATION set
                if val_metrics["wape"] < best_val_wape:
                    best_val_wape = val_metrics["wape"]
                    best_model_name = model_name
                    best_forecaster_obj = forecaster

            except Exception as e:
                logger.error(f"Failed training {model_name}: {str(e)}", exc_info=True)
                # We do not crash the entire run if one model fails; record error
                continue

        if not results:
            raise ModelTrainingError("All candidate models failed to train.")

        # Mark best model
        for r in results:
            if r["model_name"] == best_model_name:
                r["is_best"] = True

        logger.info(f"Model selection complete. Best model is '{best_model_name}' with Val WAPE: {best_val_wape:.4f}")

        return {
            "dataset_id": dataset_id,
            "job_id": job_id,
            "trained_models": results,
            "best_model_name": best_model_name,
            "total_models_evaluated": len(results),
            "test_dates": {
                "start": str(test_df["date"].min().date()),
                "end": str(test_df["date"].max().date())
            }
        }

