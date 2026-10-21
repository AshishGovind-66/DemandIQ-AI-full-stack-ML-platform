from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class ColumnMappingConfig(BaseModel):
    date_col: str = Field(default="date", description="Name of the date column")
    target_col: str = Field(default="sales", description="Name of the sales/demand column")
    product_id_col: Optional[str] = Field(default="product_id", description="Name of the product/item ID column")
    store_id_col: Optional[str] = Field(default="store_id", description="Name of the store/location ID column")
    category_col: Optional[str] = Field(default="category", description="Name of category column")
    price_col: Optional[str] = Field(default="sell_price", description="Optional price column")
    promo_col: Optional[str] = Field(default="on_promotion", description="Optional promotion flag column")

class ValidationIssue(BaseModel):
    severity: str  # ERROR, WARNING, INFO
    field: Optional[str] = None
    message: str

class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue] = []
    row_count: int
    column_count: int
    detected_columns: List[str]
    detected_types: Dict[str, str] = {}
    missing_dates_count: int = 0
    negative_values_count: int = 0
    duplicate_rows_count: int = 0

class DataProfilingReport(BaseModel):
    dataset_id: str
    dataset_name: str
    total_rows: int
    total_columns: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_duration_days: Optional[int] = None
    unique_products_count: int = 0
    unique_stores_count: int = 0
    total_sales_volume: float = 0.0
    mean_daily_sales: float = 0.0
    median_daily_sales: float = 0.0
    std_daily_sales: float = 0.0
    zero_sales_percentage: float = 0.0
    missing_values_by_column: Dict[str, int] = {}
    duplicate_rows: int = 0
    top_products: List[Dict[str, Any]] = []
    top_stores: List[Dict[str, Any]] = []
    category_breakdown: List[Dict[str, Any]] = []
    daily_trend_sample: List[Dict[str, Any]] = []
    day_of_week_pattern: List[Dict[str, Any]] = []
    monthly_pattern: List[Dict[str, Any]] = []

class DatasetResponse(BaseModel):
    id: str
    name: str
    filename: str
    file_type: str
    file_size_bytes: int
    row_count: int
    column_count: int
    columns: List[str] = []
    column_mapping: Dict[str, Any] = {}
    created_at: str

class M5SubsetRequest(BaseModel):
    store_ids: Optional[List[str]] = Field(default=["CA_1"], description="List of stores to extract")
    item_limit: Optional[int] = Field(default=20, description="Number of items to extract (max 100 for fast processing)")
    days_limit: Optional[int] = Field(default=365, description="Number of historical days to take from end of series")

