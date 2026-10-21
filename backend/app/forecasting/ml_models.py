import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import lightgbm as lgb

from backend.app.forecasting.base import BaseForecaster
from backend.app.core.logging import logger

class LinearRegressionForecaster(BaseForecaster):
    """Linear regression baseline with L2 regularization (Ridge)."""

    def __init__(self, alpha: float = 1.0):
        super().__init__(name="linear_regression", model_type="ml")
        self.alpha = alpha
        self.model_instance = Ridge(alpha=alpha)

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "LinearRegressionForecaster":
        self.feature_names = list(X.columns)
        self.model_instance.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        preds = self.model_instance.predict(X[self.feature_names])
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {"alpha": self.alpha, "algorithm": "Ridge Regression"}

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        coefs = np.abs(self.model_instance.coef_)
        total = np.sum(coefs) if np.sum(coefs) > 0 else 1.0
        normalized = coefs / total
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names, normalized)}


class RandomForestForecaster(BaseForecaster):
    """Random Forest regressor for retail demand forecasting."""

    def __init__(self, n_estimators: int = 50, max_depth: int = 10, random_state: int = 42):
        super().__init__(name="random_forest", model_type="ml")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model_instance = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "RandomForestForecaster":
        self.feature_names = list(X.columns)
        self.model_instance.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        preds = self.model_instance.predict(X[self.feature_names])
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "algorithm": "RandomForestRegressor"
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        imps = self.model_instance.feature_importances_
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names, imps)}


class XGBoostForecaster(BaseForecaster):
    """Gradient boosted decision trees via XGBoost."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        random_state: int = 42
    ):
        super().__init__(name="xgboost", model_type="ml")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model_instance = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            n_jobs=-1,
            objective="reg:squarederror"
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "XGBoostForecaster":
        self.feature_names = list(X.columns)
        self.model_instance.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        preds = self.model_instance.predict(X[self.feature_names])
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "algorithm": "XGBRegressor"
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        imps = self.model_instance.feature_importances_
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names, imps)}


class LightGBMForecaster(BaseForecaster):
    """Fast, distributed, high performance gradient boosting via LightGBM."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        random_state: int = 42
    ):
        super().__init__(name="lightgbm", model_type="ml")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model_instance = lgb.LGBMRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            n_jobs=-1,
            verbosity=-1
        )

    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "LightGBMForecaster":
        self.feature_names = list(X.columns)
        self.model_instance.fit(X, y)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("Model is not fitted.")
        preds = self.model_instance.predict(X[self.feature_names])
        return np.clip(preds, 0.0, None)

    def get_params(self) -> Dict[str, Any]:
        return {
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "learning_rate": self.learning_rate,
            "algorithm": "LGBMRegressor"
        }

    def get_feature_importance(self) -> Dict[str, float]:
        if not self.is_fitted:
            return {}
        imps = self.model_instance.feature_importances_
        total = np.sum(imps) if np.sum(imps) > 0 else 1.0
        normalized = imps / total
        return {feat: round(float(imp), 4) for feat, imp in zip(self.feature_names, normalized)}

