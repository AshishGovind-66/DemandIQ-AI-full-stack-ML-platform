import pytest
import numpy as np
from backend.app.utils.metrics import (
    calculate_mae,
    calculate_rmse,
    calculate_wape,
    calculate_forecast_bias,
    compute_all_metrics
)

def test_mae_calculation():
    y_true = np.array([10, 20, 30])
    y_pred = np.array([12, 18, 30])
    # errors: 2, 2, 0 -> mean = 4/3 = 1.3333
    mae = calculate_mae(y_true, y_pred)
    assert round(mae, 4) == 1.3333

def test_rmse_calculation():
    y_true = np.array([10, 20, 30])
    y_pred = np.array([10, 24, 30])
    # squared error = 0 + 16 + 0 = 16 -> mean = 16/3 -> sqrt = 2.3094
    rmse = calculate_rmse(y_true, y_pred)
    assert round(rmse, 4) == 2.3094

def test_wape_standard():
    y_true = np.array([10, 20, 30])  # sum = 60
    y_pred = np.array([12, 20, 28])  # abs err = 2 + 0 + 2 = 4
    # wape = 4 / 60 = 0.0667
    wape = calculate_wape(y_true, y_pred)
    assert round(wape, 4) == 0.0667

def test_wape_zero_actual_sum():
    # When sum(y) is 0 and predictions are 0 -> perfect forecast
    assert calculate_wape(np.array([0, 0, 0]), np.array([0, 0, 0])) == 0.0
    # When sum(y) is 0 and predictions > 0 -> 1.0 (100% penalty)
    assert calculate_wape(np.array([0, 0, 0]), np.array([5, 0, 0])) == 1.0

def test_forecast_bias():
    y_true = np.array([10, 10, 10])  # sum = 30
    y_pred_over = np.array([12, 12, 12])  # sum = 36 -> error sum = +6 -> bias = +0.20
    assert round(calculate_forecast_bias(y_true, y_pred_over), 2) == 0.20

    y_pred_under = np.array([8, 8, 8])  # sum = 24 -> error sum = -6 -> bias = -0.20
    assert round(calculate_forecast_bias(y_true, y_pred_under), 2) == -0.20

def test_compute_all_metrics():
    y_t = [10, 15, 20]
    y_p = [11, 14, 20]
    res = compute_all_metrics(y_t, y_p)
    assert "mae" in res
    assert "rmse" in res
    assert "wape" in res
    assert "bias" in res
    assert res["test_rows"] == 3

