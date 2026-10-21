import pandas as pd
from typing import Tuple, List
from backend.app.utils.exceptions import DatasetValidationError

def chronological_split(
    df: pd.DataFrame,
    date_col: str = "date",
    validation_days: int = 14,
    test_days: int = 14
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Splits DataFrame chronologically into train, validation, and test sets.
    Prevents data leakage by strictly partitioning on temporal cutoffs.
    """
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
    
    unique_dates = sorted(df[date_col].dt.date.unique())
    total_days = len(unique_dates)
    
    required_min_days = validation_days + test_days + 14  # At least 14 days for training
    if total_days < required_min_days:
        raise DatasetValidationError(
            f"Dataset has only {total_days} unique days. "
            f"At least {required_min_days} days are required for train ({required_min_days - validation_days - test_days}d), "
            f"validation ({validation_days}d), and test ({test_days}d) splits."
        )
    
    test_cutoff_date = unique_dates[-test_days]
    val_cutoff_date = unique_dates[-(test_days + validation_days)]
    
    train_mask = df[date_col].dt.date < val_cutoff_date
    val_mask = (df[date_col].dt.date >= val_cutoff_date) & (df[date_col].dt.date < test_cutoff_date)
    test_mask = df[date_col].dt.date >= test_cutoff_date
    
    train_df = df[train_mask].sort_values(date_col).reset_index(drop=True)
    val_df = df[val_mask].sort_values(date_col).reset_index(drop=True)
    test_df = df[test_mask].sort_values(date_col).reset_index(drop=True)
    
    return train_df, val_df, test_df

