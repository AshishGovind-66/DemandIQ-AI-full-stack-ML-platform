import pytest
import math
from backend.app.inventory.optimization_engine import InventoryOptimizationEngine
from backend.app.schemas.inventory import InventoryOptimizationRequest

def test_z_score_retrieval():
    assert round(InventoryOptimizationEngine.get_z_score(0.95), 2) == 1.64
    assert round(InventoryOptimizationEngine.get_z_score(0.99), 2) == 2.33
    # Higher service level must have strictly higher z-score
    assert InventoryOptimizationEngine.get_z_score(0.99) > InventoryOptimizationEngine.get_z_score(0.95)

def test_inventory_optimization_logic(sample_sales_df):
    req = InventoryOptimizationRequest(
        dataset_id="test-dataset",
        lead_time_days=7,
        service_level=0.95,
        default_current_stock=10.0,
        min_order_quantity=5,
        pack_size=5
    )
    summary = InventoryOptimizationEngine.optimize(
        historical_df=sample_sales_df,
        request=req
    )
    assert summary.total_products_analyzed == 2
    assert len(summary.recommendations) == 2
    
    rec = summary.recommendations[0]
    # Check LTD = daily_mean * lead_time
    assert round(rec.expected_lead_time_demand, 1) == round(rec.daily_demand_mean * 7, 1)
    # Check ROP = LTD + SS within small rounding margin
    assert abs(rec.reorder_point - (rec.expected_lead_time_demand + rec.safety_stock)) <= 0.2
    # Check pack size multiple: suggested order qty must be multiple of 5
    assert rec.suggested_order_qty % 5 == 0
    # Current stock is 10, check inventory position
    assert rec.inventory_position == 10.0

def test_moq_and_pack_size_constraint(sample_sales_df):
    req = InventoryOptimizationRequest(
        dataset_id="test-dataset",
        lead_time_days=7,
        service_level=0.95,
        default_current_stock=0.0,  # Zero stock forces reorder
        min_order_quantity=50,
        pack_size=12
    )
    summary = InventoryOptimizationEngine.optimize(
        historical_df=sample_sales_df,
        request=req
    )
    for rec in summary.recommendations:
        if rec.suggested_order_qty > 0:
            assert rec.suggested_order_qty >= 50
            assert rec.suggested_order_qty % 12 == 0
