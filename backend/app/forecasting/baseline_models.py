import numpy as np
import pandas as pd
from typing import Dict, Any
from backend.app.forecasting.base import BaseForecaster

class NaiveForecaster(BaseForecaster):
    """
    Naive baseline: forecasts demand as the most recent observed sales (lag_1).
    """

    def __init__(self):
        super().__init__(name="naive", model_type="baseline")
        self.default_value = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "NaiveForecaster":
        self.default_value = float(np.mean(y)) if len(y) > 0 else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        if "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.default_value).values
        else:
            preds = np.full(len(X), self.default_value)
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {"strategy": "last_known_value", "default_value": self.default_value}


class SeasonalNaiveForecaster(BaseForecaster):
    """
    Seasonal Naive baseline: forecasts demand based on the same day last week (lag_7).
    """

    def __init__(self, season_length: int = 7):
        super().__init__(name="seasonal_naive", model_type="baseline")
        self.season_length = season_length
        self.default_value = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "SeasonalNaiveForecaster":
        self.default_value = float(np.mean(y)) if len(y) > 0 else 0.0
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        target_lag = f"lag_{self.season_length}"
        if target_lag in X.columns:
            preds = X[target_lag].fillna(self.default_value).values
        elif "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.default_value).values
        else:
            preds = np.full(len(X), self.default_value)
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {
            "strategy": "seasonal_lag",
            "season_length": self.season_length,
            "default_value": self.default_value
        }

