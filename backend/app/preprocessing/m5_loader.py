import os
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.utils.exceptions import DatasetValidationError

class M5DataLoader:
    """Configurable and memory-safe loader for the Walmart M5 dataset."""

    @classmethod
    def get_search_directories(cls) -> List[Path]:
        """Order of directories to search for Walmart M5 files."""
        return [
            settings.DATA_RAW_DIR,
            settings.M5_DIR,
            settings.PROJECT_ROOT / "data" / "raw",
            settings.PROJECT_ROOT / "m5-forecasting-accuracy"
        ]

    @classmethod
    def find_file(cls, filename: str) -> Optional[Path]:
        """Locates an M5 file across search directories."""
        for directory in cls.get_search_directories():
            target = directory / filename
            if target.exists() and target.is_file():
                return target
        return None

    @classmethod
    def get_status(cls) -> Dict[str, any]:
        """Checks presence and sizes of M5 files."""
        expected_files = [
            "calendar.csv",
            "sales_train_validation.csv",
            "sell_prices.csv",
            "sales_train_evaluation.csv"
        ]
        status = {}
        for f in expected_files:
            path = cls.find_file(f)
            if path:
                status[f] = {
                    "available": True,
                    "path": str(path),
                    "size_mb": round(path.stat().st_size / (1024 * 1024), 2)
                }
            else:
                status[f] = {
                    "available": False,
                    "path": None,
                    "size_mb": 0.0
                }
        
        all_core_present = status["calendar.csv"]["available"] and status["sales_train_validation.csv"]["available"]
        return {
            "all_core_present": all_core_present,
            "files": status
        }

    @classmethod
    def extract_subset(
        cls,
        store_ids: Optional[List[str]] = None,
        item_limit: int = 15,
        days_limit: int = 180,
        output_filename: str = "m5_extracted_subset.csv"
    ) -> pd.DataFrame:
        """
        Extracts a clean, manageable long-format subset from M5 data.
        Keeps memory footprint low by filtering during initial read.
        """
        sales_path = cls.find_file("sales_train_validation.csv")
        calendar_path = cls.find_file("calendar.csv")
        prices_path = cls.find_file("sell_prices.csv")

        if not sales_path or not calendar_path:
            raise DatasetValidationError("Required M5 files (sales_train_validation.csv, calendar.csv) not found.")

        if not store_ids:
            store_ids = ["CA_1"]

        logger.info(f"Extracting M5 subset: stores={store_ids}, items={item_limit}, days={days_limit}")

        # 1. Read metadata columns and identify available days
        df_meta = pd.read_csv(sales_path, nrows=5)
        d_cols = [c for c in df_meta.columns if c.startswith("d_")]
        if days_limit and days_limit < len(d_cols):
            selected_d_cols = d_cols[-days_limit:]
        else:
            selected_d_cols = d_cols

        usecols = ["id", "item_id", "dept_id", "cat_id", "store_id", "state_id"] + selected_d_cols

        # 2. Read only matching stores and limit items
        df_sales = pd.read_csv(sales_path, usecols=usecols)
        df_sales = df_sales[df_sales["store_id"].isin(store_ids)]
        
        # Take top items by total sales in this period
        sales_sum = df_sales[selected_d_cols].sum(axis=1)
        top_indices = sales_sum.sort_values(ascending=False).head(item_limit).index
        df_sales_subset = df_sales.loc[top_indices].copy()

        # 3. Melt from wide to long format
        id_vars = ["item_id", "cat_id", "store_id"]
        df_long = pd.melt(
            df_sales_subset,
            id_vars=id_vars,
            value_vars=selected_d_cols,
            var_name="d",
            value_name="sales"
        )

        # 4. Merge with calendar
        df_cal = pd.read_csv(calendar_path, usecols=["date", "wm_yr_wk", "d", "event_name_1", f"snap_{store_ids[0].split('_')[0]}"])
        snap_col = f"snap_{store_ids[0].split('_')[0]}"
        df_long = df_long.merge(df_cal, on="d", how="left")

        # 5. Merge with sell_prices if available
        if prices_path:
            try:
                df_prices = pd.read_csv(prices_path)
                df_prices = df_prices[
                    df_prices["store_id"].isin(store_ids) & 
                    df_prices["item_id"].isin(df_sales_subset["item_id"].unique())
                ]
                df_long = df_long.merge(df_prices, on=["store_id", "item_id", "wm_yr_wk"], how="left")
            except Exception as e:
                logger.warning(f"Could not merge prices: {e}")
                df_long["sell_price"] = 1.0

        if "sell_price" not in df_long.columns or df_long["sell_price"].isna().all():
            df_long["sell_price"] = 1.0
        else:
            df_long["sell_price"] = df_long["sell_price"].fillna(1.0)

        # Construct canonical columns
        df_long["on_promotion"] = 0
        if snap_col in df_long.columns:
            df_long["on_promotion"] = (df_long[snap_col] == 1).astype(int)
        if "event_name_1" in df_long.columns:
            has_event = df_long["event_name_1"].notna().astype(int)
            df_long["on_promotion"] = np.maximum(df_long["on_promotion"], has_event)

        canonical_df = pd.DataFrame({
            "date": pd.to_datetime(df_long["date"]),
            "product_id": df_long["item_id"].astype(str),
            "store_id": df_long["store_id"].astype(str),
            "category": df_long["cat_id"].astype(str),
            "sales": df_long["sales"].astype(float),
            "sell_price": df_long["sell_price"].astype(float),
            "on_promotion": df_long["on_promotion"].astype(int)
        })

        canonical_df = canonical_df.sort_values(by=["date", "product_id"]).reset_index(drop=True)
        
        # Save to processed folder
        out_path = settings.DATA_PROCESSED_DIR / output_filename
        canonical_df.to_csv(out_path, index=False)
        logger.info(f"Extracted subset saved to {out_path} with {len(canonical_df)} records.")
        return canonical_df

