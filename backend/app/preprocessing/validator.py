import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from backend.app.schemas.dataset import ValidationResult, ValidationIssue, ColumnMappingConfig

class DatasetValidator:
    """Validates arbitrary retail sales datasets for forecasting compatibility."""
    
    MIN_REQUIRED_ROWS = 30
    MAX_RECOMMENDED_ROWS = 500000

    @classmethod
    def validate_dataframe(
        cls,
        df: pd.DataFrame,
        mapping: Optional[ColumnMappingConfig] = None
    ) -> ValidationResult:
        if mapping is None:
            mapping = ColumnMappingConfig()

        issues: List[ValidationIssue] = []
        row_count, col_count = df.shape
        detected_columns = df.columns.tolist()
        detected_types = {col: str(df[col].dtype) for col in df.columns}
        
        # 1. Row count check
        if row_count == 0:
            issues.append(ValidationIssue(
                severity="ERROR",
                field="rows",
                message="Dataset is completely empty (0 rows)."
            ))
            return ValidationResult(
                is_valid=False,
                issues=issues,
                row_count=0,
                column_count=col_count,
                detected_columns=detected_columns,
                detected_types=detected_types
            )

        if row_count < cls.MIN_REQUIRED_ROWS:
            issues.append(ValidationIssue(
                severity="ERROR",
                field="rows",
                message=f"Dataset contains only {row_count} rows. A minimum of {cls.MIN_REQUIRED_ROWS} is required."
            ))

        # 2. Check Date Column
        if mapping.date_col not in df.columns:
            # Try fuzzy matching date column
            possible_dates = [c for c in df.columns if any(k in c.lower() for k in ["date", "timestamp", "day", "time"])]
            hint = f" Did you mean '{possible_dates[0]}'?" if possible_dates else ""
            issues.append(ValidationIssue(
                severity="ERROR",
                field=mapping.date_col,
                message=f"Configured date column '{mapping.date_col}' not found in dataset.{hint}"
            ))
        else:
            # Check parseability of date
            sample_dates = df[mapping.date_col].dropna().head(100)
            try:
                pd.to_datetime(sample_dates)
            except Exception as e:
                issues.append(ValidationIssue(
                    severity="ERROR",
                    field=mapping.date_col,
                    message=f"Date column '{mapping.date_col}' could not be parsed as dates: {str(e)}"
                ))

        # 3. Check Target / Sales Column
        if mapping.target_col not in df.columns:
            possible_targets = [c for c in df.columns if any(k in c.lower() for k in ["sales", "demand", "quantity", "units", "qty"])]
            hint = f" Did you mean '{possible_targets[0]}'?" if possible_targets else ""
            issues.append(ValidationIssue(
                severity="ERROR",
                field=mapping.target_col,
                message=f"Configured target column '{mapping.target_col}' not found in dataset.{hint}"
            ))
        else:
            # Check numeric conversion
            numeric_target = pd.to_numeric(df[mapping.target_col], errors="coerce")
            nan_count = int(numeric_target.isna().sum())
            if nan_count > 0:
                issues.append(ValidationIssue(
                    severity="WARNING",
                    field=mapping.target_col,
                    message=f"{nan_count} values in '{mapping.target_col}' are non-numeric or missing and will be treated as zero or imputed."
                ))
            
            # Check negative sales
            neg_count = int((numeric_target.dropna() < 0).sum())
            if neg_count > 0:
                issues.append(ValidationIssue(
                    severity="WARNING",
                    field=mapping.target_col,
                    message=f"Found {neg_count} negative demand values (e.g. returns). These will be clipped to 0."
                ))

        # 4. Check Duplicate records
        id_cols = [c for c in [mapping.date_col, mapping.product_id_col, mapping.store_id_col] if c and c in df.columns]
        duplicate_count = 0
        if len(id_cols) >= 2:
            duplicate_count = int(df.duplicated(subset=id_cols).sum())
            if duplicate_count > 0:
                issues.append(ValidationIssue(
                    severity="WARNING",
                    field="duplicates",
                    message=f"Found {duplicate_count} duplicate records for key combination {id_cols}. Duplicate dates for same product/store will be summed."
                ))

        # 5. Missing values check
        missing_counts = df.isna().sum()
        for col, missing_n in missing_counts.items():
            if missing_n > 0:
                pct = round((missing_n / row_count) * 100, 2)
                issues.append(ValidationIssue(
                    severity="INFO" if pct < 10 else "WARNING",
                    field=col,
                    message=f"Column '{col}' has {missing_n} missing values ({pct}%)."
                ))

        has_errors = any(i.severity == "ERROR" for i in issues)
        
        return ValidationResult(
            is_valid=not has_errors,
            issues=issues,
            row_count=row_count,
            column_count=col_count,
            detected_columns=detected_columns,
            detected_types=detected_types,
            negative_values_count=int((pd.to_numeric(df[mapping.target_col], errors="coerce") < 0).sum()) if mapping.target_col in df.columns else 0,
            duplicate_rows_count=duplicate_count
        )

