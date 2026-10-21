from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ShapExplanationRequest(BaseModel):
    model_id: str
    sample_size: int = Field(default=200, ge=20, le=2000, description="Max samples for SHAP value computation")
    product_id: Optional[str] = Field(default=None, description="Optional product to explain")

class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float
    description: str

class ProductDriverItem(BaseModel):
    feature: str
    feature_value: float
    shap_value: float
    impact_direction: str  # POSITIVE, NEGATIVE

class ShapExplanationResponse(BaseModel):
    model_id: str
    model_name: str
    is_supported: bool
    summary_message: str
    global_feature_importance: List[FeatureImportanceItem] = []
    top_drivers_summary: List[str] = []
    product_level_sample: Optional[Dict[str, Any]] = None

