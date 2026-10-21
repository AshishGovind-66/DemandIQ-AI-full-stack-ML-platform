from typing import Dict, Type, List, Optional
from backend.app.forecasting.base import BaseForecaster
from backend.app.forecasting.baseline_models import NaiveForecaster, SeasonalNaiveForecaster
from backend.app.forecasting.ml_models import (
    LinearRegressionForecaster,
    RandomForestForecaster,
    XGBoostForecaster,
    LightGBMForecaster
)

class ModelRegistry:
    """Central registry for discovering and instantiating forecasting models."""

    _models: Dict[str, Type[BaseForecaster]] = {
        "naive": NaiveForecaster,
        "seasonal_naive": SeasonalNaiveForecaster,
        "linear_regression": LinearRegressionForecaster,
        "random_forest": RandomForestForecaster,
        "xgboost": XGBoostForecaster,
        "lightgbm": LightGBMForecaster
    }

    @classmethod
    def register(cls, name: str, forecaster_cls: Type[BaseForecaster]) -> None:
        """Dynamically registers a new forecasting model."""
        cls._models[name.lower()] = forecaster_cls

    @classmethod
    def get(cls, name: str, **kwargs) -> BaseForecaster:
        """Instantiates a forecaster by key with given kwargs."""
        name_key = name.lower()
        if name_key not in cls._models:
            raise ValueError(f"Model '{name}' is not registered. Available models: {cls.list_models()}")
        return cls._models[name_key](**kwargs)

    @classmethod
    def list_models(cls) -> List[str]:
        """Lists all registered model names."""
        return list(cls._models.keys())

    @classmethod
    def is_available(cls, name: str) -> bool:
        return name.lower() in cls._models

