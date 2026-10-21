import pandas as pd
import numpy as np
from typing import Optional, Dict
from backend.app.schemas.dataset import ColumnMappingConfig
from backend.app.utils.exceptions import DatasetValidationError

class ColumnMapper:
    """Transforms raw user or standard CSV columns into canonical DemandIQ format."""
    
    CANONICAL_COLUMNS = [
        "date",
        "product_id",
        "store_id",
        "category",
        "sales",
        "sell_price",
        "on_promotion"
    ]

    @classmethod
    def auto_detect_mapping(cls, columns: list[str]) -> ColumnMappingConfig:
        """Heuristically infers column mappings from column headers."""
        cols_lower = {c.lower(): c for c in columns}
        
        def find_col(candidates: list[str], default: Optional[str] = None) -> Optional[str]:
            # Exact match first
            for cand in candidates:
                if cand in cols_lower:
                    return cols_lower[cand]
            # Substring match second
            for col_orig in columns:
                cl = col_orig.lower()
                if any(cand in cl for cand in candidates):
                    return col_orig
            return default

        # Date detection
        date_candidates = ["date", "timestamp", "day", "datetime", "sales_date", "order_date"]
        date_col = find_col(date_candidates, default=columns[0] if columns else "date")
        
        # Target detection
        target_candidates = ["sales", "demand", "units", "quantity", "qty", "sold"]
        target_col = find_col(target_candidates, default="sales")
        
        # Product detection
        prod_candidates = ["product_id", "item_id", "sku", "product", "item", "article_id", "product_code"]
        product_id_col = find_col(prod_candidates, default=None)
        
        # Store detection
        store_candidates = ["store_id", "store", "location_id", "shop_id", "warehouse_id", "branch_id"]
        store_id_col = find_col(store_candidates, default=None)
        
        # Category detection
        cat_candidates = ["category", "dept_id", "department", "cat_id", "category_name", "group"]
        category_col = find_col(cat_candidates, default=None)
        
        # Price detection
        price_candidates = ["sell_price", "price", "unit_price", "selling_price", "cost"]
        price_col = find_col(price_candidates, default=None)
        
        # Promotion detection
        promo_candidates = ["on_promotion", "promo", "is_promo", "event", "promotion", "snap"]
        promo_col = find_col(promo_candidates, default=None)
        
        return ColumnMappingConfig(
            date_col=date_col,
            target_col=target_col,
            product_id_col=product_id_col,
            store_id_col=store_id_col,
            category_col=category_col,
            price_col=price_col,
            promo_col=promo_col
        )

    @classmethod
    def apply_mapping(
        cls,
        df: pd.DataFrame,
        mapping: ColumnMappingConfig
    ) -> pd.DataFrame:
        """Maps and standardizes raw DataFrame to canonical schema."""
        if mapping.date_col not in df.columns:
            raise DatasetValidationError(f"Missing required date column: '{mapping.date_col}'")
        if mapping.target_col not in df.columns:
            raise DatasetValidationError(f"Missing required sales/demand column: '{mapping.target_col}'")
        
        clean_df = pd.DataFrame()
        
        # 1. Date
        clean_df["date"] = pd.to_datetime(df[mapping.date_col], errors="coerce")
        if clean_df["date"].isna().all():
            raise DatasetValidationError(f"Failed to parse any valid dates from column '{mapping.date_col}'")
        
        # 2. Sales / Demand
        clean_df["sales"] = pd.to_numeric(df[mapping.target_col], errors="coerce").fillna(0.0)
        # Clip negative demand (returns) to 0 for inventory & demand modeling
        clean_df["sales"] = np.clip(clean_df["sales"], 0.0, None)
        
        # 3. Product ID
        if mapping.product_id_col and mapping.product_id_col in df.columns:
            clean_df["product_id"] = df[mapping.product_id_col].astype(str).str.strip()
        else:
            clean_df["product_id"] = "ALL_PRODUCTS"
            
        # 4. Store ID
        if mapping.store_id_col and mapping.store_id_col in df.columns:
            clean_df["store_id"] = df[mapping.store_id_col].astype(str).str.strip()
        else:
            clean_df["store_id"] = "ALL_STORES"
            
        # 5. Category
        if mapping.category_col and mapping.category_col in df.columns:
            clean_df["category"] = df[mapping.category_col].astype(str).str.strip()
        else:
            clean_df["category"] = "General"
            
        # 6. Price
        if mapping.price_col and mapping.price_col in df.columns:
            clean_df["sell_price"] = pd.to_numeric(df[mapping.price_col], errors="coerce").fillna(1.0)
        else:
            clean_df["sell_price"] = 1.0
            
        # 7. Promotion
        if mapping.promo_col and mapping.promo_col in df.columns:
            # Handle binary, boolean, or strings
            clean_df["on_promotion"] = pd.to_numeric(df[mapping.promo_col], errors="coerce").fillna(0).astype(int)
        else:
            clean_df["on_promotion"] = 0
            
        # Drop rows with null dates
        clean_df = clean_df.dropna(subset=["date"])
        
        # Aggregate any duplicate dates for the same product_id & store_id
        # Demand should be summed, price averaged, promo maximum
        group_cols = ["date", "product_id", "store_id", "category"]
        clean_df = clean_df.groupby(group_cols, as_index=False).agg({
            "sales": "sum",
            "sell_price": "mean",
            "on_promotion": "max"
        })
        
        # Chronological sort
        clean_df = clean_df.sort_values(by=["date", "product_id", "store_id"]).reset_index(drop=True)
        return clean_df
