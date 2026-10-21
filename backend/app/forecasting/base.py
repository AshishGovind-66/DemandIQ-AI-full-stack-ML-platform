from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

class BaseForecaster(ABC):
    """Abstract base class for all DemandIQ forecasting models."""

    def __init__(self, name: str, model_type: str = "ml"):
        self.name = name
        self.model_type = model_type  # "baseline" or "ml"
        self.is_fitted = False
        self.feature_names = []
        self.model_instance = None
        self.residual_std: float = 1.0  # Used for empirical prediction intervals

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: np.ndarray, **kwargs) -> "BaseForecaster":
        """Fits the model on training features and target."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generates point forecasts for input features."""
        pass

    def get_params(self) -> Dict[str, Any]:
        """Returns hyperparameters and configuration."""
        return {}

    def get_feature_importance(self) -> Dict[str, float]:
        """Returns feature importance if supported, otherwise empty dict."""
        return {}

    def set_residual_std(self, std_val: float) -> None:
        """Sets residual standard deviation for prediction intervals."""
        self.residual_std = max(0.01, float(std_val))

