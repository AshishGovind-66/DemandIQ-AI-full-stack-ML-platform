import pytest
import pandas as pd
from backend.app.preprocessing.validator import DatasetValidator
from backend.app.schemas.dataset import ColumnMappingConfig

def test_validate_empty_dataframe():
    df = pd.DataFrame()
    res = DatasetValidator.validate_dataframe(df)
    assert not res.is_valid
    assert any("empty" in issue.message.lower() for issue in res.issues)

def test_validate_missing_date_column():
    df = pd.DataFrame({
        "item_id": ["SKU1", "SKU2"],
        "sales": [10, 20]
    })
    mapping = ColumnMappingConfig(date_col="date", target_col="sales")
    res = DatasetValidator.validate_dataframe(df, mapping)
    assert not res.is_valid
    assert any("date" in issue.message.lower() for issue in res.issues)

def test_validate_missing_target_column():
    df = pd.DataFrame({
        "date": ["2023-01-01", "2023-01-02"],
        "product": ["P1", "P2"]
    })
    mapping = ColumnMappingConfig(date_col="date", target_col="sales")
    res = DatasetValidator.validate_dataframe(df, mapping)
    assert not res.is_valid
    assert any("target column" in issue.message.lower() for issue in res.issues)

def test_validate_negative_demand_detection():
    df = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=40),
        "sales": [10] * 38 + [-5, -2]
    })
    res = DatasetValidator.validate_dataframe(df)
    assert res.negative_values_count == 2
    assert any("negative demand" in issue.message.lower() for issue in res.issues)

def test_validate_valid_sample(sample_sales_df):
    res = DatasetValidator.validate_dataframe(sample_sales_df)
    assert res.is_valid
    assert res.row_count == len(sample_sales_df)

