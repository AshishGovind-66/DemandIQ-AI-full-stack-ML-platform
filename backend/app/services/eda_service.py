import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.schemas.dataset import DataProfilingReport

class EDAService:
    """Generates authentic exploratory statistics and charts from real loaded datasets."""

    @classmethod
    def profile_dataset(cls, df: pd.DataFrame, dataset_id: str, dataset_name: str) -> DataProfilingReport:
        df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        total_rows, total_cols = df.shape
        start_date = str(df["date"].min().date()) if not df.empty else None
        end_date = str(df["date"].max().date()) if not df.empty else None
        duration_days = (df["date"].max() - df["date"].min()).days + 1 if not df.empty else 0

        # Unique counts
        unique_prods = int(df["product_id"].nunique()) if "product_id" in df.columns else 1
        unique_stores = int(df["store_id"].nunique()) if "store_id" in df.columns else 1

        # Sales metrics
        sales_series = pd.to_numeric(df["sales"], errors="coerce").fillna(0.0)
        total_vol = float(sales_series.sum())
        mean_sales = float(sales_series.mean())
        median_sales = float(sales_series.median())
        std_sales = float(sales_series.std()) if total_rows > 1 else 0.0
        zero_pct = round(float((sales_series == 0).sum() / max(1, total_rows) * 100), 2)

        # Missing values
        missing_dict = {col: int(df[col].isna().sum()) for col in df.columns}

        # Duplicates
        id_cols = [c for c in ["date", "product_id", "store_id"] if c in df.columns]
        duplicates_n = int(df.duplicated(subset=id_cols).sum()) if id_cols else 0

        # Top products
        top_prods_df = df.groupby("product_id")["sales"].sum().reset_index().sort_values(by="sales", ascending=False).head(10)
        top_products = [
            {"product_id": str(r["product_id"]), "total_sales": round(float(r["sales"]), 1)}
            for _, r in top_prods_df.iterrows()
        ]

        # Top stores
        top_stores_df = df.groupby("store_id")["sales"].sum().reset_index().sort_values(by="sales", ascending=False).head(10)
        top_stores = [
            {"store_id": str(r["store_id"]), "total_sales": round(float(r["sales"]), 1)}
            for _, r in top_stores_df.iterrows()
        ]

        # Category breakdown
        cat_df = df.groupby("category")["sales"].sum().reset_index().sort_values(by="sales", ascending=False)
        cat_breakdown = [
            {"category": str(r["category"]), "total_sales": round(float(r["sales"]), 1)}
            for _, r in cat_df.iterrows()
        ]

        # Daily trend sample (aggregate by date)
        daily_agg = df.groupby("date")["sales"].sum().reset_index().sort_values(by="date")
        # Sample up to 90 points for smooth charting
        if len(daily_agg) > 90:
            step = len(daily_agg) // 90
            daily_sample_df = daily_agg.iloc[::step].copy()
        else:
            daily_sample_df = daily_agg

        daily_trend = [
            {"date": str(r["date"].date()), "sales": round(float(r["sales"]), 1)}
            for _, r in daily_sample_df.iterrows()
        ]

        # Day of week pattern
        df["day_name"] = df["date"].dt.day_name()
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_agg = df.groupby("day_name")["sales"].mean().reindex(dow_order).fillna(0.0).reset_index()
        dow_pattern = [
            {"day": r["day_name"][:3], "day_full": r["day_name"], "avg_sales": round(float(r["sales"]), 2)}
            for _, r in dow_agg.iterrows()
        ]

        # Monthly pattern
        df["month_name"] = df["date"].dt.strftime("%b")
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_agg = df.groupby("month_name")["sales"].mean().reindex(month_order).dropna().reset_index()
        monthly_pattern = [
            {"month": r["month_name"], "avg_sales": round(float(r["sales"]), 2)}
            for _, r in month_agg.iterrows()
        ]

        return DataProfilingReport(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            total_rows=total_rows,
            total_columns=total_cols,
            start_date=start_date,
            end_date=end_date,
            total_duration_days=duration_days,
            unique_products_count=unique_prods,
            unique_stores_count=unique_stores,
            total_sales_volume=round(total_vol, 2),
            mean_daily_sales=round(mean_sales, 2),
            median_daily_sales=round(median_sales, 2),
            std_daily_sales=round(std_sales, 2),
            zero_sales_percentage=zero_pct,
            missing_values_by_column=missing_dict,
            duplicate_rows=duplicates_n,
            top_products=top_products,
            top_stores=top_stores,
            category_breakdown=cat_breakdown,
            daily_trend_sample=daily_trend,
            day_of_week_pattern=dow_pattern,
            monthly_pattern=monthly_pattern
        )

