import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats
import joblib

from backend.app.core.logging import logger
from backend.app.forecasting.base import BaseForecaster
from backend.app.preprocessing.feature_engineering import FeatureEngineer
from backend.app.utils.exceptions import ForecastError

class ForecastPredictor:
    """
    Generates multi-step future demand forecasts with expanding uncertainty intervals.
    Maintains recursive feature integrity without target leakage.
    """

    @classmethod
    def generate_forecast(
        cls,
        artifact_path: str,
        historical_df: pd.DataFrame,
        horizon_days: int = 14,
        confidence_level: float = 0.95,
        product_ids: Optional[List[str]] = None,
        store_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Generating {horizon_days}-day forecast using artifact {artifact_path}")
        
        try:
            bundle = joblib.load(artifact_path)
        except Exception as e:
            raise ForecastError(f"Failed to load model artifact: {str(e)}")

        forecaster: BaseForecaster = bundle["forecaster"]
        feature_engineer: FeatureEngineer = bundle["feature_engineer"]
        model_name: str = bundle["model_name"]
        residual_std: float = getattr(forecaster, "residual_std", 1.0)

        # Standard normal z-score for two-sided confidence interval
        # e.g., 0.95 -> alpha=0.05 -> z ~ 1.96
        alpha = 1.0 - confidence_level
        z_score = float(stats.norm.ppf(1.0 - alpha / 2.0))

        # Filter historical data if requested
        df = historical_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        if product_ids:
            df = df[df["product_id"].isin(product_ids)]
        if store_ids:
            df = df[df["store_id"].isin(store_ids)]

        if df.empty:
            raise ForecastError("No historical data available for selected products/stores.")

        # Identify unique series
        series_combinations = df[["product_id", "store_id", "category"]].drop_duplicates().to_dict(orient="records")
        max_date = df["date"].max()
        future_dates = [max_date + pd.Timedelta(days=i) for i in range(1, horizon_days + 1)]

        forecast_rows = []
        
        # Step-by-step recursive forecasting for each product/store series
        for item in series_combinations:
            pid = item["product_id"]
            sid = item["store_id"]
            cat = item["category"]

            # Sub-dataframe for this series
            sub_df = df[(df["product_id"] == pid) & (df["store_id"] == sid)].sort_values(by="date").copy()
            # Mean sell price for this item
            item_price = float(sub_df["sell_price"].mean()) if "sell_price" in sub_df.columns and not sub_df["sell_price"].isna().all() else 1.0

            # Working history copy for appending recursive predictions
            history_buffer = sub_df.tail(60).copy()

            for h_step, f_date in enumerate(future_dates, start=1):
                # Placeholder future row
                future_row = pd.DataFrame([{
                    "date": f_date,
                    "product_id": pid,
                    "store_id": sid,
                    "category": cat,
                    "sales": 0.0,  # Will be predicted
                    "sell_price": item_price,
                    "on_promotion": 0
                }])

                # Concatenate with history to compute lag and rolling features
                eval_df = pd.concat([history_buffer, future_row], ignore_index=True)
                
                # Transform using fitted FeatureEngineer
                transformed_df = feature_engineer.transform(eval_df)
                
                # Extract features for the target future row
                X_future = transformed_df[feature_engineer.feature_names].tail(1)
                
                # Predict
                pred_val = float(forecaster.predict(X_future)[0])
                pred_val = max(0.0, round(pred_val, 2))

                # Expanding prediction interval as horizon increases
                # sqrt(1 + (h_step - 1) / 14) models growing uncertainty over multi-step forecast
                horizon_expansion_factor = np.sqrt(1.0 + (h_step - 1) / 14.0)
                margin = z_score * residual_std * horizon_expansion_factor
                lower = max(0.0, round(pred_val - margin, 2))
                upper = round(pred_val + margin, 2)

                forecast_rows.append({
                    "date": f_date.strftime("%Y-%m-%d"),
                    "product_id": pid,
                    "store_id": sid,
                    "category": cat,
                    "predicted_demand": pred_val,
                    "lower_bound": lower,
                    "upper_bound": upper
                })

                # Append prediction to history_buffer for subsequent steps
                future_row["sales"] = pred_val
                history_buffer = pd.concat([history_buffer, future_row], ignore_index=True).tail(60)

        results_df = pd.DataFrame(forecast_rows)
        total_demand = float(results_df["predicted_demand"].sum())
        mean_demand = float(results_df["predicted_demand"].mean()) if not results_df.empty else 0.0

        # Create historical comparison sample (last 30 days of actuals aggregated by date)
        hist_recent = df[df["date"] > (max_date - pd.Timedelta(days=30))].groupby("date", as_index=False)["sales"].sum()
        hist_comparison = [
            {"date": r["date"].strftime("%Y-%m-%d"), "actual_sales": round(float(r["sales"]), 2)}
            for _, r in hist_recent.iterrows()
        ]

        return {
            "model_name": model_name,
            "horizon_days": horizon_days,
            "confidence_level": confidence_level,
            "start_date": future_dates[0].strftime("%Y-%m-%d"),
            "end_date": future_dates[-1].strftime("%Y-%m-%d"),
            "total_forecasted_demand": round(total_demand, 2),
            "average_daily_demand": round(mean_demand, 2),
            "points_count": len(results_df),
            "forecast_df": results_df,
            "forecast_points_sample": results_df.head(200).to_dict(orient="records"),
            "historical_comparison": hist_comparison
        }

