import numpy as np
from typing import Dict, Union

def calculate_mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Mean Absolute Error: (1/n) * sum(|y - y_hat|)"""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) == 0:
        return 0.0
    return float(np.mean(np.abs(y_true - y_pred)))

def calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Root Mean Squared Error: sqrt((1/n) * sum((y - y_hat)^2))"""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) == 0:
        return 0.0
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

def calculate_wape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Weighted Absolute Percentage Error (WAPE):
    WAPE = sum(|y - y_hat|) / sum(y)
    
    Safely handles zero denominator:
    If sum(y) == 0:
      - If sum(|y - y_hat|) == 0, returns 0.0 (perfect zero forecast for zero demand)
      - If sum(|y - y_hat|) > 0, returns 1.0 (100% error due to over-forecasting on zero demand)
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) == 0:
        return 0.0
    
    abs_errors_sum = float(np.sum(np.abs(y_true - y_pred)))
    actual_sum = float(np.sum(y_true))
    
    if actual_sum == 0.0:
        return 0.0 if abs_errors_sum == 0.0 else 1.0
    
    return float(abs_errors_sum / actual_sum)

def calculate_forecast_bias(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Forecast Bias (Normalized Mean Error):
    Bias = sum(y_hat - y) / sum(y)
    
    Positive bias indicates over-forecasting.
    Negative bias indicates under-forecasting.
    Safely handles zero actual sum: returns 0.0 if difference is 0, else sign of difference.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    if len(y_true) == 0:
        return 0.0
    
    error_sum = float(np.sum(y_pred - y_true))
    actual_sum = float(np.sum(y_true))
    
    if actual_sum == 0.0:
        if error_sum == 0.0:
            return 0.0
        return 1.0 if error_sum > 0 else -1.0
    
    return float(error_sum / actual_sum)

def compute_all_metrics(y_true: Union[np.ndarray, list], y_pred: Union[np.ndarray, list]) -> Dict[str, float]:
    """Computes all standard demand forecasting metrics."""
    y_t = np.asarray(y_true, dtype=float)
    y_p = np.asarray(y_pred, dtype=float)
    # Clip negative predictions to zero for retail demand
    y_p = np.clip(y_p, 0.0, None)
    
    return {
        "mae": round(calculate_mae(y_t, y_p), 4),
        "rmse": round(calculate_rmse(y_t, y_p), 4),
        "wape": round(calculate_wape(y_t, y_p), 4),
        "bias": round(calculate_forecast_bias(y_t, y_p), 4),
        "test_rows": int(len(y_t))
    }

