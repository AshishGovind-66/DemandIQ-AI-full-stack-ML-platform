import pytest
import pandas as pd
import numpy as np
from backend.app.preprocessing.column_mapper import ColumnMapper
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.preprocessing.feature_engineering import FeatureEngineer
from backend.app.utils.time_series import chronological_split

def test_column_mapper_auto_detect():
    cols = ["TransactionDate", "SKU", "Store", "Qty_Sold", "UnitPrice"]
    mapping = ColumnMapper.auto_detect_mapping(cols)
    assert mapping.date_col == "TransactionDate"
    assert mapping.product_id_col == "SKU"
    assert mapping.store_id_col == "Store"
    assert mapping.target_col == "Qty_Sold"
    assert mapping.price_col == "UnitPrice"

def test_column_mapper_apply_and_clean():
    raw_df = pd.DataFrame({
        "TransactionDate": ["2023-01-01", "2023-01-01", "2023-01-02"],
        "SKU": ["A", "A", "A"],
        "Store": ["S1", "S1", "S1"],
        "Qty_Sold": [10, 5, -2],  # duplicates on 2023-01-01 should sum to 15, -2 should clip to 0
        "UnitPrice": [2.5, 3.0, 2.5]
    })
    mapping = ColumnMappingConfig(
        date_col="TransactionDate",
        target_col="Qty_Sold",
        product_id_col="SKU",
        store_id_col="Store",
        price_col="UnitPrice"
    )
    clean_df = ColumnMapper.apply_mapping(raw_df, mapping)
    
    # After deduplication and grouping: 2 rows
    assert len(clean_df) == 2
    # Summed duplicate sales on 2023-01-01
    row_1 = clean_df[clean_df["date"] == "2023-01-01"].iloc[0]
    assert row_1["sales"] == 15.0
    # Negative clipped
    row_2 = clean_df[clean_df["date"] == "2023-01-02"].iloc[0]
    assert row_2["sales"] == 0.0

def test_chronological_split_no_leakage(sample_sales_df):
    train, val, test = chronological_split(
        df=sample_sales_df,
        date_col="date",
        validation_days=14,
        test_days=14
    )
    assert train["date"].max() < val["date"].min()
    assert val["date"].max() < test["date"].min()
    assert len(test["date"].dt.date.unique()) == 14
    assert len(val["date"].dt.date.unique()) == 14

def test_feature_engineering_no_future_leakage(sample_sales_df):
    fe = FeatureEngineer()
    feat_df, names = fe.fit_transform(sample_sales_df)
    
    assert "lag_1" in feat_df.columns
    assert "lag_7" in feat_df.columns
    assert "rolling_mean_7" in feat_df.columns
    assert "is_weekend" in feat_df.columns
    
    # Check that lag_1 for second observation equals previous sales
    sku1_df = feat_df[feat_df["product_id"] == "SKU_1"].sort_values(by="date")
    assert sku1_df.iloc[1]["lag_1"] == sku1_df.iloc[0]["sales"]

