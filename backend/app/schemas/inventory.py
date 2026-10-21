from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class InventoryOptimizationRequest(BaseModel):
    dataset_id: str
    forecast_run_id: Optional[str] = Field(default=None, description="Forecast run to base demand upon")
    lead_time_days: int = Field(default=7, ge=1, le=180, description="Supplier lead time in days")
    service_level: float = Field(default=0.95, ge=0.50, le=0.999, description="Target cycle service level")
    review_period_days: int = Field(default=7, ge=1, le=90, description="Review period / order cycle in days")
    default_current_stock: Optional[float] = Field(default=None, description="Default on-hand stock if not in product table")
    default_on_order: Optional[float] = Field(default=0.0, description="Default stock already ordered/in-transit")
    holding_cost_annual_pct: float = Field(default=0.20, description="Annual inventory holding cost percentage")
    stockout_penalty_per_unit: Optional[float] = Field(default=None, description="Penalty per unit of unmet demand")
    min_order_quantity: Optional[int] = Field(default=1, description="MOQ constraint")
    pack_size: Optional[int] = Field(default=1, description="Pack size multiple constraint")
    item_overrides: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Per-item overrides for current_stock, lead_time, unit_cost, etc."
    )

class ItemInventoryRecommendation(BaseModel):
    product_id: str
    store_id: Optional[str] = None
    category: Optional[str] = None
    unit_price: float = 0.0
    daily_demand_mean: float
    daily_demand_std: float
    lead_time_days: int
    service_level: float
    z_score: float
    expected_lead_time_demand: float
    safety_stock: float
    reorder_point: float
    current_on_hand: float
    on_order: float
    inventory_position: float
    target_stock: float
    suggested_order_qty: int
    stockout_risk: bool
    excess_stock_risk: bool
    days_of_supply_remaining: float
    estimated_holding_cost: float = 0.0

class InventoryOptimizationSummary(BaseModel):
    plan_id: str
    dataset_id: str
    lead_time_days: int
    service_level: float
    total_products_analyzed: int
    items_at_stockout_risk: int
    items_with_excess_stock: int
    total_suggested_reorder_units: int
    total_estimated_reorder_value: float
    total_holding_cost_estimate: float
    recommendations: List[ItemInventoryRecommendation] = []

