from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
import shap
import joblib

from backend.app.core.logging import logger
from backend.app.schemas.explainability import (
    ShapExplanationResponse,
    FeatureImportanceItem,
    ProductDriverItem
)

FEATURE_DESCRIPTIONS = {
    "lag_1": "Sales volume on previous day (t-1)",
    "lag_7": "Sales volume exactly 1 week ago (t-7)",
    "lag_14": "Sales volume 2 weeks ago (t-14)",
    "lag_28": "Sales volume 4 weeks ago (t-28)",
    "rolling_mean_7": "7-day moving average demand",
    "rolling_mean_14": "14-day moving average demand",
    "rolling_mean_28": "28-day moving average demand",
    "rolling_std_7": "7-day demand volatility (standard deviation)",
    "rolling_std_28": "28-day demand volatility",
    "sell_price": "Unit selling price of the item",
    "on_promotion": "Whether item was on promotion / special event",
    "day_of_week": "Day of the week (0=Mon, 6=Sun)",
    "is_weekend": "Weekend indicator (Saturday/Sunday)",
    "month": "Month of the year (seasonal baseline)",
    "dow_sin": "Cyclical sine representation of weekday",
    "dow_cos": "Cyclical cosine representation of weekday",
    "product_id_encoded": "Specific product identifier encoding",
    "store_id_encoded": "Store location identifier encoding",
    "category_encoded": "Merchandise category encoding"
}

class ShapExplainerService:
    """Computes SHAP explanations and feature drivers for trained ML models."""

    @classmethod
    def explain(
        cls,
        artifact_path: str,
        sample_df: pd.DataFrame,
        sample_size: int = 150,
        product_id: Optional[str] = None
    ) -> ShapExplanationResponse:
        logger.info(f"Computing SHAP explanations for artifact {artifact_path} with sample_size={sample_size}")
        
        try:
            bundle = joblib.load(artifact_path)
        except Exception as e:
            return ShapExplanationResponse(
                model_id="",
                model_name="unknown",
                is_supported=False,
                summary_message=f"Could not load model artifact: {str(e)}"
            )

        model_name = bundle.get("model_name", "unknown")
        forecaster = bundle.get("forecaster")
        feature_names = bundle.get("feature_names", [])
        fe = bundle.get("feature_engineer")

        # Baseline models check
        if bundle.get("model_type") == "baseline" or model_name in ["naive", "seasonal_naive"]:
            return ShapExplanationResponse(
                model_id=bundle.get("model_id", ""),
                model_name=model_name,
                is_supported=False,
                summary_message=(
                    f"'{model_name}' is a heuristic rule-based baseline (e.g. lag_1 or lag_7). "
                    "Rule-based baselines do not have statistical weights or gradient trees to explain via SHAP. "
                    "Train an ML model such as XGBoost, LightGBM, or Random Forest to view SHAP feature importances."
                )
            )

        if not hasattr(forecaster, "model_instance") or forecaster.model_instance is None:
            return ShapExplanationResponse(
                model_id=bundle.get("model_id", ""),
                model_name=model_name,
                is_supported=False,
                summary_message=f"Model instance not found in artifact for {model_name}."
            )

        # Prepare evaluation sample
        try:
            df_eval = sample_df.copy()
            if product_id and "product_id" in df_eval.columns:
                sub = df_eval[df_eval["product_id"] == product_id]
                if not sub.empty:
                    df_eval = sub

            # Transform features
            feat_df = fe.transform(df_eval) if fe else df_eval
            X_eval = feat_df[feature_names].copy()
            
            # Subsample for computational performance
            if len(X_eval) > sample_size:
                X_sample = X_eval.sample(n=sample_size, random_state=42)
            else:
                X_sample = X_eval

            raw_model = forecaster.model_instance
            
            # Tree-based or linear explainer
            if model_name in ["xgboost", "lightgbm", "random_forest"]:
                explainer = shap.TreeExplainer(raw_model)
                shap_values = explainer.shap_values(X_sample)
            else:
                # Ridge / Linear
                explainer = shap.LinearExplainer(raw_model, X_sample)
                shap_values = explainer.shap_values(X_sample)

            # Compute mean absolute SHAP value for each feature
            if isinstance(shap_values, list):
                # Multiclass or list format
                shap_matrix = np.array(shap_values[0])
            else:
                shap_matrix = np.array(shap_values)

            mean_abs_shap = np.mean(np.abs(shap_matrix), axis=0)
            total_shap = float(np.sum(mean_abs_shap)) if np.sum(mean_abs_shap) > 0 else 1.0

            # Sort descending
            sorted_indices = np.argsort(mean_abs_shap)[::-1]
            
            global_importance: List[FeatureImportanceItem] = []
            top_drivers: List[str] = []

            for idx in sorted_indices[:12]:
                feat = feature_names[idx]
                score = round(float(mean_abs_shap[idx] / total_shap), 4)
                desc = FEATURE_DESCRIPTIONS.get(feat, f"Feature: {feat}")
                global_importance.append(FeatureImportanceItem(
                    feature=feat,
                    importance=score,
                    description=desc
                ))

            # Build readable summary bullet points
            if global_importance:
                top_1 = global_importance[0]
                top_2 = global_importance[1] if len(global_importance) > 1 else None
                top_drivers.append(f"Top overall demand driver: '{top_1.feature}' ({top_1.description}), accounting for {int(top_1.importance * 100)}% of model attribution.")
                if top_2:
                    top_drivers.append(f"Secondary driver: '{top_2.feature}' ({top_2.description}), contributing {int(top_2.importance * 100)}% to demand variation.")
                top_drivers.append("Note: SHAP values represent statistical attribution within this model's decision logic and should not be confused with causal proof.")

            return ShapExplanationResponse(
                model_id=bundle.get("model_id", ""),
                model_name=model_name,
                is_supported=True,
                summary_message=f"Successfully computed SHAP explanations on {len(X_sample)} representative observations.",
                global_feature_importance=global_importance,
                top_drivers_summary=top_drivers
            )

        except Exception as e:
            logger.error(f"SHAP explanation failed: {str(e)}", exc_info=True)
            # Graceful fallback: return model's built-in feature importance if available
            fallback_imp = forecaster.get_feature_importance()
            items = [
                FeatureImportanceItem(
                    feature=k,
                    importance=v,
                    description=FEATURE_DESCRIPTIONS.get(k, k)
                ) for k, v in sorted(fallback_imp.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            return ShapExplanationResponse(
                model_id=bundle.get("model_id", ""),
                model_name=model_name,
                is_supported=True,
                summary_message="Computed feature importance via model tree splits (SHAP approximation).",
                global_feature_importance=items,
                top_drivers_summary=["Feature importances derived from model decision split frequencies."]
            )

