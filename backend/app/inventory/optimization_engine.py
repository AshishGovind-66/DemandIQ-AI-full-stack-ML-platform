import math
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from scipy import stats

from backend.app.core.logging import logger
from backend.app.schemas.inventory import (
    InventoryOptimizationRequest,
    ItemInventoryRecommendation,
    InventoryOptimizationSummary
)
from backend.app.utils.exceptions import InventoryError

class InventoryOptimizationEngine:
    """
    Mathematical inventory optimization engine computing:
    - Expected Lead-Time Demand (LTD)
    - Lead-Time Demand Variance / Standard Deviation
    - Safety Stock (SS) with user-selected Cycle Service Level (CSL)
    - Reorder Point (ROP)
    - Inventory Position (On-hand + On-order)
    - Suggested Replenishment Order Quantity subject to MOQ & Pack-size constraints
    - Stockout & Excess Inventory risks
    """

    # Service Level to Standard Normal Z-Score map (one-sided)
    SERVICE_LEVEL_Z = {
        0.90: 1.2816,
        0.95: 1.6449,
        0.98: 2.0537,
        0.99: 2.3263,
        0.999: 3.0902
    }

    @classmethod
    def get_z_score(cls, service_level: float) -> float:
        """Computes or retrieves standard normal quantile for cycle service level."""
        sl_rounded = round(service_level, 3)
        if sl_rounded in cls.SERVICE_LEVEL_Z:
            return cls.SERVICE_LEVEL_Z[sl_rounded]
        # Otherwise compute from normal CDF inverse
        return float(stats.norm.ppf(service_level))

    @classmethod
    def optimize(
        cls,
        historical_df: pd.DataFrame,
        request: InventoryOptimizationRequest,
        forecast_df: Optional[pd.DataFrame] = None
    ) -> InventoryOptimizationSummary:
        logger.info(f"Running inventory optimization with lead_time={request.lead_time_days}d, CSL={request.service_level}")

        if historical_df.empty:
            raise InventoryError("Cannot run inventory optimization on empty historical dataset.")

        df = historical_df.copy()
        if not pd.api.types.is_datetime64_any_dtype(df["date"]):
            df["date"] = pd.to_datetime(df["date"])

        z = cls.get_z_score(request.service_level)
        lead_time = request.lead_time_days
        review_period = request.review_period_days
        sqrt_lead_time = math.sqrt(lead_time)

        # Unique products to analyze
        unique_items = df[["product_id", "store_id", "category"]].drop_duplicates().to_dict(orient="records")
        recommendations: List[ItemInventoryRecommendation] = []

        total_reorder_units = 0
        total_reorder_value = 0.0
        total_holding_cost = 0.0
        stockout_count = 0
        excess_count = 0

        # Optional item overrides
        overrides = request.item_overrides or {}

        for item in unique_items:
            pid = item["product_id"]
            sid = item["store_id"]
            cat = item.get("category", "General")

            item_override = overrides.get(pid, {})

            # Filter data for this item
            item_df = df[(df["product_id"] == pid) & (df["store_id"] == sid)].sort_values(by="date")
            
            # Unit price
            if "unit_cost" in item_override:
                unit_price = float(item_override["unit_cost"])
            elif "sell_price" in item_df.columns and not item_df["sell_price"].isna().all():
                unit_price = float(item_df["sell_price"].mean())
            else:
                unit_price = 10.0

            # Item lead time (default or override)
            item_lead_time = item_override.get("lead_time_days", lead_time)
            item_sqrt_lt = math.sqrt(item_lead_time)

            # Demand statistics
            # If forecast is provided, we use forecast mean for expected future demand
            if forecast_df is not None and not forecast_df.empty:
                fc_sub = forecast_df[(forecast_df["product_id"] == pid) & (forecast_df["store_id"] == sid)]
                if not fc_sub.empty:
                    daily_mean = float(fc_sub["predicted_demand"].mean())
                else:
                    daily_mean = float(item_df["sales"].mean()) if not item_df.empty else 0.0
            else:
                daily_mean = float(item_df["sales"].mean()) if not item_df.empty else 0.0

            # Empirical daily demand std dev from historical sales
            daily_std = float(item_df["sales"].std()) if len(item_df) > 1 else max(0.5, daily_mean * 0.3)
            if math.isnan(daily_std) or daily_std == 0.0:
                daily_std = max(0.5, daily_mean * 0.2)

            # 1. Expected Lead-Time Demand (LTD)
            expected_ltd = daily_mean * item_lead_time

            # 2. Safety Stock (SS)
            # Under fixed lead-time with independent daily demand errors:
            # SS = z * sigma_D * sqrt(L)
            safety_stock = z * daily_std * item_sqrt_lt

            # 3. Reorder Point (ROP)
            # ROP = LTD + SS
            reorder_point = expected_ltd + safety_stock

            # 4. Target Stock Level (Order-up-to level S for periodic review)
            # Protection period = Lead Time + Review Period
            # S = daily_mean * (L + R) + z * daily_std * sqrt(L + R)
            protection_period = item_lead_time + review_period
            target_stock = (daily_mean * protection_period) + (z * daily_std * math.sqrt(protection_period))

            # 5. Inventory on hand & on order
            # If user provided default or override, use it; otherwise use realistic simulated stock (1.2 * ROP)
            if "current_stock" in item_override:
                current_on_hand = float(item_override["current_stock"])
            elif request.default_current_stock is not None:
                current_on_hand = float(request.default_current_stock)
            else:
                # Default baseline heuristic: slightly above or below ROP for realistic distribution
                current_on_hand = round(max(0.0, float(np.random.normal(reorder_point * 1.05, safety_stock * 0.4))), 1)

            on_order = float(item_override.get("on_order", request.default_on_order or 0.0))
            
            # Inventory Position = On-Hand + On-Order
            inventory_position = current_on_hand + on_order

            # 6. Suggested Order Quantity (Order-up-to policy)
            # If inventory position <= reorder point, replenish up to target stock
            if inventory_position <= reorder_point:
                raw_order_qty = max(0.0, target_stock - inventory_position)
            else:
                raw_order_qty = 0.0

            # Apply MOQ and Pack Size constraints
            moq = item_override.get("min_order_quantity", request.min_order_quantity or 1)
            pack_size = item_override.get("pack_size", request.pack_size or 1)
            
            final_order_qty = 0
            if raw_order_qty > 0:
                constrained_qty = max(raw_order_qty, float(moq))
                # Round up to nearest pack size
                final_order_qty = int(math.ceil(constrained_qty / pack_size) * pack_size)

            # 7. Stockout and Excess Indicators
            stockout_risk = bool(inventory_position <= reorder_point)
            days_of_supply = round(current_on_hand / daily_mean, 1) if daily_mean > 0 else 999.0
            excess_stock_risk = bool(days_of_supply > 60.0 or inventory_position > (2.5 * max(1.0, target_stock)))

            if stockout_risk:
                stockout_count += 1
            if excess_stock_risk:
                excess_count += 1

            # 8. Costs
            # Annual holding cost = holding_cost_pct * unit_price * average_cycle_inventory
            # average_inventory ~ safety_stock + (order_qty / 2)
            holding_pct = request.holding_cost_annual_pct
            avg_inv = safety_stock + (final_order_qty / 2.0 if final_order_qty > 0 else daily_mean * review_period / 2.0)
            holding_cost_annual = round(avg_inv * unit_price * holding_pct, 2)

            total_reorder_units += final_order_qty
            total_reorder_value += final_order_qty * unit_price
            total_holding_cost += holding_cost_annual

            rec = ItemInventoryRecommendation(
                product_id=pid,
                store_id=sid,
                category=cat,
                unit_price=round(unit_price, 2),
                daily_demand_mean=round(daily_mean, 2),
                daily_demand_std=round(daily_std, 2),
                lead_time_days=int(item_lead_time),
                service_level=float(request.service_level),
                z_score=round(z, 4),
                expected_lead_time_demand=round(expected_ltd, 1),
                safety_stock=round(safety_stock, 1),
                reorder_point=round(reorder_point, 1),
                current_on_hand=round(current_on_hand, 1),
                on_order=round(on_order, 1),
                inventory_position=round(inventory_position, 1),
                target_stock=round(target_stock, 1),
                suggested_order_qty=int(final_order_qty),
                stockout_risk=stockout_risk,
                excess_stock_risk=excess_stock_risk,
                days_of_supply_remaining=days_of_supply,
                estimated_holding_cost=holding_cost_annual
            )
            recommendations.append(rec)

        import uuid
        plan_id = str(uuid.uuid4())
        
        return InventoryOptimizationSummary(
            plan_id=plan_id,
            dataset_id=request.dataset_id,
            lead_time_days=request.lead_time_days,
            service_level=request.service_level,
            total_products_analyzed=len(recommendations),
            items_at_stockout_risk=stockout_count,
            items_with_excess_stock=excess_count,
            total_suggested_reorder_units=int(total_reorder_units),
            total_estimated_reorder_value=round(total_reorder_value, 2),
            total_holding_cost_estimate=round(total_holding_cost, 2),
            recommendations=recommendations
        )

