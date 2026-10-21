import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.preprocessing import LabelEncoder
from backend.app.core.logging import logger

class FeatureEngineer:
    """
    Leakage-free time-series feature engineering pipeline.
    Constructs calendar, cyclical, lag, and rolling statistics.
    Ensures that features at time t strictly use observations <= t-1.
    """

    LAG_DAYS = [1, 7, 14, 28]
    ROLLING_WINDOWS = [7, 14, 28]

    def __init__(self):
        self.encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.categorical_cols: List[str] = ["product_id", "store_id", "category"]
        self.is_fitted: bool = False

    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Fits encoders on training data and transforms DataFrame."""
        transformed_df = self._create_features(df, is_training=True)
        self.is_fitted = True
        return transformed_df, self.feature_names

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforms inference or validation DataFrame using fitted encoders."""
        if not self.is_fitted:
            raise ValueError("FeatureEngineer must be fitted before calling transform.")
        return self._create_features(df, is_training=False)

    def _create_features(self, df: pd.DataFrame, is_training: bool = True) -> pd.DataFrame:
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        # 1. Sort chronologically
        df = df.sort_values(by=["product_id", "store_id", "date"]).reset_index(drop=True)

        # 2. Calendar Features
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)

        # Cyclical transformations
        df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7.0)
        df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7.0)
        df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12.0)

        # 3. Categorical Encoding (Label Encoding with Unknown handling)
        for col in self.categorical_cols:
            if col in df.columns:
                if is_training:
                    le = LabelEncoder()
                    df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
                    self.encoders[col] = le
                else:
                    le = self.encoders.get(col)
                    if le:
                        known_classes = set(le.classes_)
                        # Map unseen classes to the first known class or -1
                        series_str = df[col].astype(str)
                        safe_series = series_str.map(lambda s: s if s in known_classes else le.classes_[0])
                        df[f"{col}_encoded"] = le.transform(safe_series)
                    else:
                        df[f"{col}_encoded"] = 0
            else:
                df[f"{col}_encoded"] = 0

        # 4. Lag and Rolling Window Features (Per Product & Store series)
        # To avoid data leakage, rolling stats use shifted sales series (shift(1))
        # so target y_t is NEVER included in rolling features for time t.
        grouped = df.groupby(["product_id", "store_id"])["sales"]

        # Lags
        for lag in self.LAG_DAYS:
            col_name = f"lag_{lag}"
            df[col_name] = grouped.shift(lag)

        # Shifted series for rolling calculations
        sales_shifted_1 = grouped.shift(1)

        # Rolling statistics
        for w in self.ROLLING_WINDOWS:
            # Group again on the shifted series
            temp_df = pd.DataFrame({
                "product_id": df["product_id"],
                "store_id": df["store_id"],
                "shifted_sales": sales_shifted_1
            })
            shifted_grouped = temp_df.groupby(["product_id", "store_id"])["shifted_sales"]
            
            df[f"rolling_mean_{w}"] = shifted_grouped.transform(lambda s: s.rolling(w, min_periods=1).mean())
            df[f"rolling_std_{w}"] = shifted_grouped.transform(lambda s: s.rolling(w, min_periods=1).std()).fillna(0.0)

        # Fill any remaining NaNs in lag/rolling features with 0.0 (e.g. beginning of time series)
        feature_cols_to_fill = [f"lag_{lag}" for lag in self.LAG_DAYS] + \
                              [f"rolling_mean_{w}" for w in self.ROLLING_WINDOWS] + \
                              [f"rolling_std_{w}" for w in self.ROLLING_WINDOWS]
        
        for col in feature_cols_to_fill:
            df[col] = df[col].fillna(0.0)

        # 5. Price & Promotion
        if "sell_price" not in df.columns:
            df["sell_price"] = 1.0
        if "on_promotion" not in df.columns:
            df["on_promotion"] = 0

        # Assemble list of feature names
        if is_training:
            candidate_features = [
                "day_of_week",
                "day_of_month",
                "month",
                "is_weekend",
                "dow_sin",
                "dow_cos",
                "month_sin",
                "month_cos",
                "product_id_encoded",
                "store_id_encoded",
                "category_encoded",
                "sell_price",
                "on_promotion"
            ] + feature_cols_to_fill
            self.feature_names = candidate_features

        return df

    def get_features_and_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """Separates feature matrix X and target vector y."""
        X = df[self.feature_names].copy()
        y = df["sales"].values
        return X, y

